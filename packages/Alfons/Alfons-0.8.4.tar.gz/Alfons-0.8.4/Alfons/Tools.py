import Alfons
import socket
import time
import threading
import logging
import os
import json
import string
import random

log = logging.getLogger("alfons")

def findServer(**kwargs):
	"Find the server and register"
	global info
	
	discoverRequestString = Alfons.ACPRequest("discover", {"destination": "alfons"}, {}, createRequestId()).export()

	broadcastSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	broadcastSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	broadcastSocket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

	def broadcast():
		stopBroadcast = False
		while not stopBroadcast:
			try:
				broadcastSocket.sendto(discoverRequestString, (kwargs.get("ip", "255.255.255.255"), 27373))
			except:
				stopBroadcast = True
				break
			time.sleep(3)

	broadcastThread = threading.Thread(target=broadcast)
	broadcastThread.daemon = True
	broadcastThread.start()
	
	if kwargs.get("receiveMultiple", False):
		servers = []

		def receive(servers):
			while True:
				try:
					data, addr = broadcastSocket.recvfrom(2028)
					servers += [(data, addr)]
				except:
					break

		receiveThread = threading.Thread(target=receive, args=(servers, ))
		receiveThread.daemon = True
		receiveThread.start()

		time.sleep(3)
		broadcastSocket.close()
		items = []

		for data, addr in servers:
			body = Alfons.ACPResponse.initFromString(data).body
			body["id"] = body["public_key"][71:112].replace("\n", "")
			body["ip"] = "%s:%s" % addr
			items.append(body)

		return items 
	else:
		data, addr = broadcastSocket.recvfrom(2028)
		broadcastSocket.close()
		response = Alfons.ACPResponse.initFromString(data)
		return (addr[0], Alfons.Crypt.AlfonsRSA.importKey(response.body["public_key"]))

def register():
	body = {"id": Alfons.info["device_id"], "name": Alfons.info["name"], "description": Alfons.info["description"], "public_key": Alfons.info["public_key"].exportKey()}
	return Alfons.request("register", "alfons", body, callback="return")

def createRequestId():
		"Generate a request id"
		return "".join(random.choice(string.ascii_uppercase + string.digits) for _ in range(20))

def createErrorResponse(message, requestId):
	"Create a response string with an error message"
	return Alfons.ACPResponse({"destination": Alfons.info["device_id"], "sender": "alfons", "success": False, "message": message}, {}, requestId)

def listen(run, **kwargs):
	"Listen for a message from the server"
	if kwargs.get("forId", False):
		Alfons.deviceSocket.settimeout(kwargs.get("timeout", 7))
	else:
		Alfons.deviceSocket.settimeout(None)

	while True:
		try:
			data, addr = Alfons.deviceSocket.recvfrom(2028)
		except socket.timeout: # Timeout will only occur if 'forId' is set due to 'deviceSocket.settimeout(kwargs.get("timeout", 7))'
			requestId = kwargs.get("forId")
			response = createErrorResponse("Timed out", requestId)
			if requestId in Alfons.requests:
				Alfons.requests[requestId]["callback"](response)
				Alfons.requests.pop(requestId)
			return response

		if not data.startswith("ACP/" + Alfons.ACP_VERSION):
			(data, signature) = Alfons.Crypt.decrypt(data)
			if not Alfons.Crypt.AlfonsRSA.verify(data, signature, Alfons.info["alfons_key"]):
				print "Not valid"
				continue

		r = decodeR(data)
		
		if not r:
			continue

		if r["type"] == "request":
			if not run is None:
				request = Alfons.ACPRequest(r["command"], r["headers"], r["body"], r["request_id"])

				try:
					d = run(request)
					if d is None:
						log.warn("Didn't get any data from command (%s)" % request.command)

					data = d if d is not None else ({"success": False, "message": "Didn't get any data from command"}, {})

					if not isinstance(d, tuple):
						data = (data, {})
				except:
					log.critical("Error executing command (%s) on IoT" % request.command, exc_info=1)
					data = ({"success": False, "message": "Error executing command on IoT"}, {})
				
				
				data[0]["destination"] = request.headers["sender"]

				response = Alfons.ACPResponse(data[0], data[1], request.requestId)
				
				Alfons.send(response.export())
			else:
				response = Alfons.ACPResponse({"sender": Alfons.info["device_id"], "destination": r["headers"]["sender"], "success": False, "message": "This device does not take any commands (right now)"}, {}, r["request_id"])
				Alfons.send(response.export())
		else:
			response = Alfons.ACPResponse(r["headers"], r["body"], r["request_id"])
			forId = kwargs.get("forId", False)
			
			if response.requestId in Alfons.requests:
				Alfons.requests[response.requestId]["callback"](response)
				if response.requestId in Alfons.requests:
					Alfons.requests.pop(response.requestId)

			if forId == response.requestId:
				return response

def eradicate():
	"Send an eradicate request to the server and listen for the response"
	log.info("Eradicating")
	r = Alfons.request("eradicate", "alfons", {"id": Alfons.info["device_id"]})
	return listen(None, forId=r.requestId)

def decodeR(r, sender = None):
	"Decode a request or response to a dict"
	requestId = ""
	headers = {}
	body = {}

	response = {}
	
	try:
		parts = r.split("\n\n", 1)
		sHeaders = parts[0].split("\n")
		sBody = parts[1]
		topRow = sHeaders.pop(0).split(" ")
		
		# Remove the first object (protocol), and get the last (id)
		topRow.pop(0)
		requestId = topRow.pop()
		
		response["request_id"] = requestId

		# If it's a request there will be a command
		if len(topRow) == 1:
			response["type"] = "request"
			response["command"] = topRow.pop()
		else:
			response["type"] = "response"

		# Convert the headers to a dict
		for h in sHeaders:
			parts = h.split(": ")
			key = parts[0].lower()
			value = parts[1]

			if value == "True":
				value = True
			elif value == "False":
				value = False

			headers[key] = value
		
		response["headers"] = headers
		
		if r.startswith("ACP/"):
			body = json.loads(sBody)
			response["body"] = body
			response["protocol"] = "ACP"
		elif r.startswith("ATP/"):
			response["content"] = sBody
			response["protocol"] = "ATP"
		
		response["headers"]["sender"] = Alfons.Tools.escapeDeviceId(response["headers"]["sender"])

	except:
		print "Not valid ACP/" + Alfons.ACP_VERSION
		return {}

	return response

def readSettings(path, defaultSettings = {}):
	settingsPath = path + "/settings.json"

	if not os.path.isfile(settingsPath):
		with open(settingsPath, "w+") as f:
			f.write("{}")

	with open(settingsPath, "r+") as f:
		try:
			settings = json.load(f)
		except:
			settings = {}

	for k in defaultSettings:
		if k not in settings:
			settings[k] = defaultSettings[k]

	for s in settings:
		Alfons.info[s] = settings[s]

def writeSettings(path, settingsKeys):
	settings = {}

	for k in settingsKeys:
		settings[k] = Alfons.info[k]

	with open(path + "/settings.json", "w+") as f:
		json.dump(settings, f)

def escapeDeviceId(deviceId):
	return deviceId.replace("\n", "").replace("+", "-").replace("/", "_")