import Alfons
import threading
import time
import socket

def setUpATPListener(requestId, transportCallback):
	Alfons.requests[requestId + "_atp"] = {}
	Alfons.requests[requestId + "_atp"]["callback"] = transportCallback
	Alfons.requests[requestId + "_atp"]["timestamp"] = int(time.time())
	
	def getATPData():
		atpClient = setUpATPClient(requestId)
		data = recvFullATP(atpClient)
		
		response = Alfons.Atp.ATPMessage.initFromString(data)
		Alfons.requests[requestId + "_atp"]["callback"](response)
		Alfons.requests.pop(requestId + "_atp")
	
	atpThread = threading.Thread(target=getATPData)
	atpThread.daemon = True
	atpThread.start()

def setUpATPClient(requestId, destination = None):
	"Set up an ATP client with defined mode. Enter a destination to use send mode, otherwise it will receive"
	client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	ip = "" if not "ip" in Alfons.info else Alfons.info["ip"]
	client.connect((ip, Alfons.info["port"]))
	
	if destination:
		initString = "ATP/" + Alfons.ATP_VERSION + " initsend " + requestId + "\nSender: " + Alfons.info["device_id"] + "\nDestination: " + destination + "\nContent-length: 0\n\n"
	else:
		initString = "ATP/" + Alfons.ATP_VERSION + " initrecv " + requestId + "\nSender: " + Alfons.info["device_id"] + "\nContent-length: 0\n\n"

	if not ip.startswith("192.168."):
		initString = Alfons.Crypt.encrypt(initString, Alfons.info["alfons_key"]) + "\n\n"
	
	client.sendall(initString)

	return client

def recvFullATP(connection):
	data = ""

	# while (notEncryped and not receivedFullContentLength) or (encrypted and not receivedEnd)
	while (data.startswith("ATP/") and not getATPContentLength(data) == getATPContentLengthHeader(data)) or (not data.startswith("ATP/") and not data.endswith("\n\n")):
		data += connection.recv(1)
	
	if not data.startswith("ATP/"):
		return Alfons.Crypt.decrypt(data)
	
	return str(data)

def transportString(s, destination, requestId):
	client = setUpATPClient(requestId, destination)
	
	transportString = "ATP/" + Alfons.ATP_VERSION + " transfer " + requestId + " \nSender: " + Alfons.info["device_id"] + "\nContent-length: " + str(len(s)) + "\n\n" + s

	if "ip" in Alfons.info and not Alfons.info["ip"].startswith("192.168."):
		transportString = Alfons.Crypt.encrypt(transportString, Alfons.info["alfons_key"]) + "\n\n"
	
	client.sendall(transportString)
	
	client.close()

def getATPContentLengthHeader(s):
	lines = s.split("\n")
	i = 0
	for l in lines:
		l2 = l.split(": ")
		if l2[0].lower() == "content-length" and len(lines) > i + 1:
			return int(l2[1])
		i+= 1

def getATPContentLength(s):
	parts = s.split("\n\n")

	if len(parts) >= 2:
		return len(parts[1])

	return -1

class ATPMessage:
	"An object holding all info about a response"
	
	def __init__(self, headers, content, requestId):
		"Set info from components"
		self.headers = headers
		self.content = content
		self.requestId = requestId

		if not "sender" in self.headers:
			self.headers["sender"] = Alfons.info["device_id"]

	@staticmethod
	def initFromString(s):
		"Set info from a string"
		r = Alfons.Tools.decodeR(s)

		if r["protocol"] != "ATP":
			return None

		return ATPMessage(r["headers"], r["content"], r["request_id"])

	def export(self):
		"Export the object to a string"

		version = Alfons.ATP_VERSION
		responseString = "ATP/" + version + " " + self.requestId

		for h in self.headers:
			responseString += "\n" + h.capitalize() + ": " + str(self.headers[h])

		responseString += "\n\n" + self.content

		return responseString