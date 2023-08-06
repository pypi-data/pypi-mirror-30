#!/usr/bin/python

from websocket import WebSocket
ws = WebSocket()
ws.connect("ws://localhost:8080/websocket")
print "Sending 'Hello, World'..."
ws.send("Hello, World")
print "Sent"
print "Reeiving..."
result =  ws.recv()
print "Received '%s'" % result
ws.close()