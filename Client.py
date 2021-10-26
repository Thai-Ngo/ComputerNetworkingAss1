from tkinter import *
import tkinter.messagebox
from PIL import Image, ImageTk
import socket, threading, sys, traceback, os

from RtpPacket import RtpPacket

import time

CACHE_FILE_NAME = "Cache/cache-"
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
	DESCRIBE = 4
	
	# Initiation..
	def __init__(self, master, serveraddr, serverport, rtpport, filename):
		self.master = master
		self.master.protocol("WM_DELETE_WINDOW", self.handler)
		self.serverAddr = serveraddr
		self.serverPort = int(serverport)
		self.rtpPort = int(rtpport)
		self.fileName = filename
		self.cachefile = ''
		# This attributes are used for maintain the screen
		self.lostPacket = 0
		self.receivePacket = 0
		self.packetLossRate = StringVar()
		self.videoDataRate = StringVar()
		self.fps = StringVar()
  		# self.fps.set("FPS: 0.00")
		# self.videoDataRate.set("0.00kps")
		self.totalDataIn1Sec = 0
		self.counter = 0
		self.createWidgets()
		# This attributes are used for the RTP packet
		self.rtspSeq = 0
		self.sessionId = 0
		self.requestSent = -1
		self.teardownAcked = 0
		self.connectToServer()
		self.frameNbr = 0
		self.setupMovie()
		
	# THIS GUI IS JUST FOR REFERENCE ONLY, STUDENTS HAVE TO CREATE THEIR OWN GUI 	
	def createWidgets(self):
		"""Build GUI."""
		# Create Setup button
		# self.setup = Button(self.master, width=20, padx=3, pady=3)
		# self.setup["text"] = "Setup"
		# self.setup["command"] = self.setupMovie
		# self.setup.grid(row=2, column=0, padx=2, pady=2)

		# Create Describe button
		self.describe = Button(self.master, width=20, padx=3, pady=3)
		self.describe["text"] = "Describe"
		self.describe["command"] = self.describeMovie
		self.describe.grid(row=2, column=0, padx=2, pady=2)
  
		# Create Play button		
		self.start = Button(self.master, width=20, padx=3, pady=3)
		self.start["text"] = "Play"
		self.start["command"] = self.playMovie
		self.start.grid(row=2, column=1, padx=2, pady=2)
		
		# Create Pause button			
		self.pause = Button(self.master, width=20, padx=3, pady=3)
		self.pause["text"] = "Pause"
		self.pause["command"] = self.pauseMovie
		self.pause.grid(row=2, column=2, padx=2, pady=2)
	
		# Create Teardown button
		self.teardown = Button(self.master, width=20, padx=3, pady=3)
		self.teardown["text"] = "Stop"
		self.teardown["command"] =  self.exitClient
		self.teardown.grid(row=2, column=3, padx=2, pady=2)
		
		# Create a label to display the movie
		self.label = Label(self.master, height=19)
		self.label.grid(row=1, column=0, columnspan=4, sticky=W+E+N+S, padx=5, pady=5) 
  
		# Create a label to display movie's name
		self.title = Label(self.master, height=2, text=self.fileName)
		self.title.grid(row=0, column=1, columnspan=2, padx=2, pady=2)
  
		# Create a label to display the packet loss rate
		self.lTitle = Label(self.master, height=2, text="Packet loss rate")
		self.lTitle.grid(row=3, column=0, padx=2, pady=2)
  
		self.lossRate = Label(self.master, height=2, textvariable=self.packetLossRate)
		self.lossRate.grid(row=3, column=1, padx=2, pady=2)
  
		# Create a label to display the video data rate
		self.vTitle = Label(self.master, height=2, text="Video data rate")
		self.vTitle.grid(row=3, column=2, padx=2, pady=2)
  
		self.dataRate = Label(self.master, height=2, textvariable=self.videoDataRate)
		self.dataRate.grid(row=3, column=3, padx=2, pady=2)
  
		# Create a label to display the video FPS
		self.fTitle = Label(self.master, height=2, textvariable=self.fps)
		self.fTitle.grid(row=0, column=0, padx=2, pady=2)

	def setupMovie(self):
		"""Setup button handler."""
	#TODO
		if (self.state == self.INIT):
			self.sendRtspRequest(self.SETUP)
   
	def describeMovie(self):
		"""Describe button handler."""
		if (self.state == self.READY):
			self.sendRtspRequest(self.DESCRIBE)
	
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
		self.cachefile = CACHE_FILE_NAME + str(self.sessionId) + CACHE_FILE_EXT
  
		if (self.state == self.READY):
			self.event = threading.Event()
			self.event.clear()
			threading.Thread(target=self.listenRtp).start()
			self.sendRtspRequest(self.PLAY)
	
	def listenRtp(self):		
		"""Listen for RTP packets."""
		#TODO
		self.time = float(time.time())
		while True:
			try:
				data, addr = self.rtpSocket.recvfrom(20480)	
				if data:
					rtpPacket = RtpPacket()
					rtpPacket.decode(data)
					self.updateMovie(self.writeFrame(rtpPacket.getPayload()))
     				
					# Calculate the packet loss rate
					prev = self.frameNbr
					self.frameNbr = rtpPacket.seqNum()

					diff = self.frameNbr - prev - 1
					if diff >= 0 :
						self.lostPacket += diff
						if diff == 1:
							print("Lost 1 packet")
						elif diff > 1:
							print("Lost", diff, "packets")
       
					self.receivePacket += 1	
					print("Receive packer number", self.frameNbr - 1)
						
					lostRate = float(self.lostPacket) / (self.lostPacket + self.receivePacket) * 100
					self.packetLossRate.set(str(round(lostRate, 2)) + "%")

					# Calculate the video data rate and fps
					currTime = float(time.time())
					self.totalDataIn1Sec += len(rtpPacket.getPacket())
					self.counter += 1
					
					if (currTime - self.time > 1.0) :		
						dataRate = self.totalDataIn1Sec / (currTime - self.time) * 8 / 1024
						fps = self.counter / (currTime - self.time)
						self.videoDataRate.set(str(round(dataRate, 2)) + "kps")
						self.fps.set("FPS: " + str(round(fps, 2)))
						self.time = currTime
						self.totalDataIn1Sec = 0
						self.counter = 0

			except:
				if self.event.isSet():
					break
				if self.teardownAcked == 1:
					self.rtpSocket.close()
					self.teardownAcked = 0
					time.sleep(0.5)
					break
 
		self.lostPacket = 0
		self.receivePacket = 0
		self.frameNbr = 0
		self.totalDataReiceive = 0
		self.counter = 0
		print("--------------------")
		print("END RTP THREAD\n")
	
	def annouce(self, data):
		tkinter.messagebox.showinfo(title="Session description", message=data)
 
	def writeFrame(self, data):
		"""Write the received frame to a temp image file. Return the image file."""
	#TODO
		f = open(self.cachefile, "wb")
		f.write(data)
		f.close()
		return self.cachefile

	def updateMovie(self, imageFile):
		"""Update the image file as video frame in the GUI."""
	#TODO
		photo = ImageTk.PhotoImage(Image.open(imageFile))
		self.label.configure(image = photo, height=300)
		self.label.image = photo
		
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
			self.rtspSeq += 1
			data = 'PLAY ' + self.fileName + ' RTSP/1.0\nCSeq: ' + str(self.rtspSeq) + '\nSession: ' + str(self.sessionId) 
		elif (requestCode == self.PAUSE):
			self.rtspSeq += 1
			data = 'PAUSE ' + self.fileName + ' RTSP/1.0\nCSeq: ' + str(self.rtspSeq) + '\nSession: ' + str(self.sessionId) 
		elif (requestCode == self.TEARDOWN):
			self.rtspSeq += 1
			data = 'TEARDOWN ' + self.fileName + ' RTSP/1.0\nCSeq: ' + str(self.rtspSeq) + '\nSession: ' + str(self.sessionId) 
		elif (requestCode == self.DESCRIBE):	
			self.rtspSeq += 1
			data = 'DESCRIBE ' + self.fileName + ' RTSP/1.0\nCSeq: ' + str(self.rtspSeq) + '\nSession: ' + str(self.sessionId) 
			
		self.clientSocket.send(data.encode())
	
	
	def recvRtspReply(self):
		"""Receive RTSP reply from the server."""
		#TODO
		while self.requestSent != self.TEARDOWN:
			msg = self.clientSocket.recv(1024)
			if msg:
				print(msg.decode("utf-8"))
				status, data = self.parseRtspReply(msg.decode("utf-8"))
				if (status == 200):
					if (self.requestSent == self.SETUP):
						print("receive SETUP\n")
						self.state = self.READY
						self.openRtpPort()
					elif (self.requestSent == self.PLAY):
						print("receive PLAY\n")
						self.state = self.PLAYING
					elif (self.requestSent == self.PAUSE):
						print("receive READY\n")
						self.state = self.READY
					elif (self.requestSent == self.TEARDOWN):
						print("receive TEARDOWN\n")
						self.state = self.INIT
						self.teardownAcked = 1
					elif (self.requestSent == self.DESCRIBE):
						print("receive DESCRIBE\n")
						self.annouce(data)
						
		print("--------------------")
		print("END LISTENING READ\n")
	
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

		info = ''
		if (len(request) > 3):
			info = request[3] + '\n' + request[4]
		return int(line0[1]), info
			
  
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
			self.rtpSocket.bind(('', self.rtpPort))
			print(self.rtpPort)
			print("Connection Success")
		except:
			print("Connection Error")
		

	def handler(self):
		"""Handler on explicitly closing the GUI window."""
		#TODO
		self.exitClient()
		self.clientSocket.close()
		if self.cachefile != '':
			os.remove(self.cachefile)
		time.sleep(1)
		exit()