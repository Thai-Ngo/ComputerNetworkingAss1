from tkinter import *
import tkinter.messagebox
from PIL import Image, ImageTk
import socket, threading, sys, traceback, os

from RtpPacket import RtpPacket

import time

CACHE_FILE_NAME = "cache-"
CACHE_FILE_EXT = ".jpg"

class Client:
	INIT = 0
	READY = 1
	PLAYING = 2
	state = INIT
	
	SETUP = 0
	PLAY = 1
	PAUSE = 2
	TEARDOWN = 3
	
	# Initiation..
	def __init__(self, master, serveraddr, serverport, rtpport, filename):
		self.master = master
		self.master.protocol("WM_DELETE_WINDOW", self.handler)
		self.createWidgets()
		self.serverAddr = serveraddr
		self.serverPort = int(serverport)
		self.rtpPort = int(rtpport)
		self.fileName = filename
		self.rtspSeq = 0
		self.sessionId = 0
		self.requestSent = -1
		self.teardownAcked = 0
		self.connectToServer()
		self.frameNbr = 0
		
	# THIS GUI IS JUST FOR REFERENCE ONLY, STUDENTS HAVE TO CREATE THEIR OWN GUI 	
	def createWidgets(self):
		"""Build GUI."""
		# Create Setup button
		self.setup = Button(self.master, width=20, padx=3, pady=3)
		self.setup["text"] = "Setup"
		self.setup["command"] = self.setupMovie
		self.setup.grid(row=1, column=0, padx=2, pady=2)
		
		# Create Play button		
		self.start = Button(self.master, width=20, padx=3, pady=3)
		self.start["text"] = "Play"
		self.start["command"] = self.playMovie
		self.start.grid(row=1, column=1, padx=2, pady=2)
		
		# Create Pause button			
		self.pause = Button(self.master, width=20, padx=3, pady=3)
		self.pause["text"] = "Pause"
		self.pause["command"] = self.pauseMovie
		self.pause.grid(row=1, column=2, padx=2, pady=2)
		
		# Create Teardown button
		self.teardown = Button(self.master, width=20, padx=3, pady=3)
		self.teardown["text"] = "Teardown"
		self.teardown["command"] =  self.exitClient
		self.teardown.grid(row=1, column=3, padx=2, pady=2)
		
		# Create a label to display the movie
		self.label = Label(self.master, height=19)
		self.label.grid(row=0, column=0, columnspan=4, sticky=W+E+N+S, padx=5, pady=5) 
	
	def setupMovie(self):
		"""Setup button handler."""
	#TODO
		if (self.state == self.INIT):
			self.sendRtspRequest(self.SETUP)
	
	def exitClient(self):
		"""Teardown button handler."""
	#TODO
		if (self.state != self.INIT):
			self.sendRtspRequest(self.TEARDOWN)

	def pauseMovie(self):
		"""Pause button handler."""
	#TODO
		if (self.state == self.PLAYING):
			self.sendRtspRequest(self.PAUSE)
	
	def playMovie(self):
		"""Play button handler."""
	#TODO
		if (self.state == self.READY):
			self.event = threading.Event()
			self.event.clear()
			threading.Thread(target=self.listenRtp).start()
			self.sendRtspRequest(self.PLAY)
	
	def listenRtp(self):		
		"""Listen for RTP packets."""
		#TODO
		print("\nListening\n")
		while True:
			try:
				data, addr = self.rtpSocket.recvfrom(20480)	
				if data:
					print(data)
			except:
				if self.event.isSet():
					break
				if self.teardownAcked == 1:
					self.rtpSocket.close()
					self.teardownAcked = 0
					break
		
					
	def writeFrame(self, data):
		"""Write the received frame to a temp image file. Return the image file."""
	#TODO
	
	def updateMovie(self, imageFile):
		"""Update the image file as video frame in the GUI."""
	#TODO
		
	def connectToServer(self):
		"""Connect to the Server. Start a new RTSP/TCP session."""
	#TODO
		self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.clientSocket.connect((self.serverAddr, self.serverPort))
	
	def sendRtspRequest(self, requestCode):
		"""Send RTSP request to the server."""	
		#-------------
		# TO COMPLETE
		#-------------
		data = ''
		self.requestSent = requestCode
		if (requestCode == self.SETUP):
			listener = threading.Thread(target=self.recvRtspReply) 
			listener.start()
   
			self.rtspSeq = 1
			data = 'SETUP ' + self.fileName + ' RTSP/1.0\nCSeq: ' + str(self.rtspSeq) + '\nTransport: RTP/UDP; client_port= ' + str(self.rtpPort)  
		elif (requestCode == self.PLAY):
			self.rtspSeq = self.rtspSeq + 1
			data = 'PLAY ' + self.fileName + ' RTSP/1.0\nCSeq: ' + str(self.rtspSeq) + '\nSession: ' + str(self.sessionId) 
		elif (requestCode == self.PAUSE):
			self.rtspSeq = self.rtspSeq + 1
			data = 'PAUSE ' + self.fileName + ' RTSP/1.0\nCSeq: ' + str(self.rtspSeq) + '\nSession: ' + str(self.sessionId) 
		elif (requestCode == self.TEARDOWN):
			self.rtspSeq = self.rtspSeq + 1
			data = 'TEARDOWN ' + self.fileName + ' RTSP/1.0\nCSeq: ' + str(self.rtspSeq) + '\nSession: ' + str(self.sessionId) 
			
		self.clientSocket.send(data.encode())
	
	
	def recvRtspReply(self):
		"""Receive RTSP reply from the server."""
		#TODO
		while self.requestSent != self.TEARDOWN:
			msg = self.clientSocket.recv(1024)
			if msg:
				print(msg.decode("utf-8"))
				status = self.parseRtspReply(msg.decode("utf-8"))
				if (status == 200):
					if (self.requestSent == self.SETUP):
						self.state = self.READY
						self.openRtpPort()
					elif (self.requestSent == self.PLAY):
						self.state = self.PLAYING
					elif (self.requestSent == self.PAUSE):
						self.state = self.READY
					elif (self.requestSent == self.TEARDOWN):
						self.state = self.INIT
						self.teardownAcked = 1

	
	def parseRtspReply(self, data):
		"""Parse the RTSP reply from the server."""
		#TODO
		request = data.split('\n')
		line1 = request[1].split(' ')
		seqNum = int(line1[1])
  
		if seqNum == self.rtspSeq:
			line2 = request[2].split(' ')
			self.sessionId = int(line2[1])	

		line0 = request[0].split(' ')
		return int(line0[1])
			
  
	def openRtpPort(self):
		"""Open RTP socket binded to a specified port."""
		#-------------
		# TO COMPLETE
		#-------------
		# Create a new datagram socket to receive RTP packets from the server
		# self.rtpSocket = ...
		
		# Set the timeout value of the socket to 0.5sec
		# ...
		self.rtpSocket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
		self.rtpSocket.settimeout(0.5)
		try:
			self.rtpSocket.bind((self.serverAddr, self.rtpPort))
			print(self.serverAddr, self.rtpPort)
			print("\nConnection Success\n")
		except:
			print("\nConnection Error\n")
		

	def handler(self):
		"""Handler on explicitly closing the GUI window."""
		#TODO
		self.exitClient()
		self.clientSocket.close()
		exit()
