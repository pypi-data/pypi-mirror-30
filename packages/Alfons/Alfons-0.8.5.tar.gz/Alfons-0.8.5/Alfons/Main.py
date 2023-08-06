#!/usr/bin/env python
# -*- coding: utf-8 -*-

import Alfons.Crypt
import Alfons.Tools as tools
import random
import string
import json
import socket
import time
import traceback
import threading
import logging
import os
import sys

ACP_VERSION = "0.6"
ATP_VERSION = "0.2"

deviceSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

info = {}
requests = {}
commands = {}

path = os.path.dirname(os.path.abspath(sys.argv[0]))

log = logging.getLogger("alfons")

logging.basicConfig(filename=path + "/" + os.path.splitext(os.path.basename(os.path.abspath(sys.argv[0])))[0] + ".log", level=logging.WARN, format="%(asctime)s %(name)s %(levelname)s %(filename)s line %(lineno)d %(funcName)s \t %(message)s", datefmt="%Y-%m-%d %H:%M:%S %z")

def request(command, dest, data, headers={}, requestId=None,  **kwargs):
	"Send a request with the command, data and headers to the destination"

	headers["sender"] = info["device_id"]
	headers["destination"] = dest
	request = ACPRequest(command, headers, data, tools.createRequestId())

	return requestRequestObject(request, **kwargs)

def requestRequestObject(request, **kwargs):
	requestId = request.requestId
	
	if kwargs.get("transportCallback", False):
		request.headers["data-transfer"] = "expected"
		
		requests[requestId + "_atp"] = {}
		requests[requestId + "_atp"]["callback"] = kwargs.get("transportCallback")
		requests[requestId + "_atp"]["timestamp"] = int(time.time())
		
		def getATPData():
			atpClient = Alfons.Atp.setUpATPClient(requestId)
			response = Alfons.Atp.ATPMessage.initFromString(Alfons.Atp.recvFullATP(atpClient))
			requests[requestId + "_atp"]["callback"](response)

		atpThread = threading.Thread(target=getATPData)
		atpThread.daemon = True	
		atpThread.start()
	
	send(request.export())
	
	if kwargs.get("callback", False):
		if kwargs.get("callback") != "return":
			requests[requestId] = {}
			requests[requestId]["callback"] = kwargs.get("callback")
			requests[requestId]["timestamp"] = int(time.time())
		
		return tools.listen(None, forId=requestId)

	return request

def send(s):
	"Encrypt a string with the server public key and send it to the server"
	if not info["ip"].startswith("192.168."):
		s = Alfons.Crypt.encrypt(s, info["alfons_key"])
	deviceSocket.sendall(s)

def connect(ip, port = 27373):
	"Connect to the ip"
	global info

	info["ip"] = ip
	info["port"] = port

	deviceSocket.connect((ip, port))

def close():
	"Close the connection to the server"
	deviceSocket.close()

class ACPRequest:
	"An object holding all information about a request"
	address = ("", 0)

	def __init__(self, command, headers, body, requestId):
		self.command = command
		self.headers = headers
		self.body = body
		self.requestId = requestId

		if not "sender" in self.headers:
			self.headers["sender"] = Alfons.info["device_id"]

	@staticmethod
	def initFromString(s):
		"Init the request object from a string"

		r = tools.decodeR(s)

		if r["protocol"] != "ACP":
			return None

		return ACPRequest(r["command"], r["headers"], r["body"], r["request_id"])

	def export(self):
		"Export the object to a string"
		
		requestString = "ACP/" + ACP_VERSION + " " + self.command + " " + self.requestId

		for h in self.headers:
			requestString += "\n" + h.capitalize() + ": " + self.headers[h]

		requestString += "\n\n" + json.dumps(self.body)
		
		return requestString

class ACPResponse:
	"An object holding all information about a response"
	
	def __init__(self, headers, body, requestId):
		self.headers = headers
		self.body = body
		self.requestId = requestId

		if not "sender" in self.headers:
			self.headers["sender"] = Alfons.info["device_id"]

	@staticmethod
	def initFromString(s):
		"Init the response object from a string"
		r = tools.decodeR(s)
		
		if r["protocol"] != "ACP":
			return None

		return ACPResponse(r["headers"], r["body"], r["request_id"])

	def export(self):
		"Export the object to a string"

		responseString = "ACP/" + ACP_VERSION + " " + self.requestId

		for h in self.headers:
			responseString += "\n" + h.capitalize() + ": " + str(self.headers[h])

		responseString += "\n\n" + json.dumps(self.body)

		return responseString