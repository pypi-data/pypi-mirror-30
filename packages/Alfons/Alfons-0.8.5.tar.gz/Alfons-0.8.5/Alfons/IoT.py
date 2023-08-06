#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Alfons import *
import traceback
import time
import logging
import json

log = logging.getLogger("IoT")

def start(name, description):
	"Start an IoT service"
	Alfons.info["name"] = name
	Alfons.info["description"] = description
	Alfons.Crypt.AlfonsRSA.getKey()

	ip, Alfons.info["alfons_key"] = Tools.findServer()

	Alfons.connect(ip)

	# Retry until the device have been allowed
	while not tools.register().headers["success"]:
		time.sleep(30)
	
	Alfons.IoT.addCommand("list", "List commands on the IoT", _commandList)

	def handler(request):
		if request.command in Alfons.commands:
			try:
				commandData = Alfons.commands[request.command]["function"](request)

				if commandData == None:
					commandData = ({"success": False}, {})

				if not isinstance(commandData, tuple):
					commandData = (commandData, {})
				
				return commandData

			except:
				log.critical("Request crashed on the IoT device", exc_info=1)
				return ({"success": False, "message": "Request crashed on the IoT device"}, {})

		return ({"success": False, "message": "Command not found"}, {})

	while True:
		try:
			tools.listen(handler)
		except KeyboardInterrupt:
			tools.eradicate()
			break
		except:
			log.critical("Crashed", exc_info=1)

def addCommand(command, description, function):
	Alfons.commands[command] = {"command": command, "description": description, "function": function}

def _commandList(request):
	if not "data-transfer" in request.headers or request.headers["data-transfer"] != "expected":
		return {"data-transfer": "required", "success": False}
	
	commands = []

	for c in Alfons.commands:
		command = Alfons.commands[c]
		commands.append({"command": command["command"], "description": command["description"]})

	Alfons.Atp.transportString(json.dumps({"items": commands}), request.headers["sender"], request.requestId)

	return {"success": True}