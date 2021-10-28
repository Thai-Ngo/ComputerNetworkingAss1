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
		self.packetLossRate.set("0.0%")
		self.videoDataRate.set("0.00kps")
		self.fps.set("0.00")
		self.totalDataIn1Sec = 0
		self.counter = 0
		self.createWidgets()
		self.playFlag = 0
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
  
		# Create Return button
		self.home = Button(self.master, width=40, padx=0, pady=0, bg='white')
		self.home["text"] = "Return"
		# self.describe["command"] = self.describeMovie
		self.home.grid(row=0, column=0, padx=2, pady=2)
		homeButtonImage = ImageTk.PhotoImage(Image.open("Image/cancelButton.png").resize((40, 40)))
		self.home.configure(image = homeButtonImage)
		self.home.image = homeButtonImage
  
		# Create a label to display movie's name
		self.mTitle = Label(self.master, height=2, text=self.fileName)
		self.mTitle.grid(row=0, column=1, columnspan=7, padx=2, pady=2)
  

		# Create a label to display the movie
		self.label = Label(self.master, height=17)
		self.label.grid(row=1, column=0, columnspan=9, sticky=W+E+N+S, padx=5, pady=5) 

		# Create a label to padding
		self.temp_0 = Label(self.master, width=10)
		self.temp_0.grid(row=2, column=0, columnspan=2,padx=3, pady=3) 
		self.temp_1 = Label(self.master, width=10)
		self.temp_1.grid(row=2, column=7, columnspan=2,padx=3, pady=3) 
  
		# Create Describe button
		self.describe = Button(self.master, width=40, padx=3, pady=3, bg='white')
		self.describe["text"] = "Describe"
		self.describe["command"] = self.describeMovie
		self.describe.grid(row=0, column=8, padx=2, pady=2)
		describeButtonImage = ImageTk.PhotoImage(Image.open("Image/infoButton.png").resize((40, 40)))
		self.describe.configure(image = describeButtonImage)
		self.describe.image = describeButtonImage
  
		# Create Reset button
		self.reset = Button(self.master, width=50, padx=3, pady=3, bg='white')
		self.reset["text"] = "Reset"
		self.reset["command"] = self.resetMovie
		self.reset.grid(row=2, column=2, padx=2, pady=2)
		resetButtonImage = ImageTk.PhotoImage(Image.open("Image/resetButton.png").resize((50, 50)))
		self.reset.configure(image = resetButtonImage)
		self.reset.image = resetButtonImage
  
		# Create Backward button		
		self.backward = Button(self.master, width=50, padx=3, pady=3, bg='white')
		self.backward["text"] = "Backward"
		self.backward["command"] = self.backwardMovie
		self.backward.grid(row=2, column=3, padx=2, pady=2)
		backwardButtonImage = ImageTk.PhotoImage(Image.open("Image/backwardButton.png").resize((50, 50)))
		self.backward.configure(image = backwardButtonImage)
		self.backward.image = backwardButtonImage
  
		# # Create Play button		
		# self.start = Button(self.master, width=60, padx=3, pady=3, bg='white')
		# self.start["text"] = "Play"
		# self.start["command"] = self.playMovie
		# self.start.grid(row=3, column=4, padx=2, pady=2)
		# startButtonImage = ImageTk.PhotoImage(Image.open("Image/playButton.png").resize((60, 60)))
		# self.start.configure(image = startButtonImage)
		# self.start.image = startButtonImage
		
		# # Create Pause button			
		# self.pause = Button(self.master, width=60, padx=3, pady=3, bg='white')
		# self.pause["text"] = "Pause"
		# self.pause["command"] = self.pauseMovie
		# self.pause.grid(row=4, column=4, padx=2, pady=2)
		# pauseButtonImage = ImageTk.PhotoImage(Image.open("Image/pauseButton.png").resize((60, 60)))
		# self.pause.configure(image = pauseButtonImage)
		# self.pause.image = pauseButtonImage
  
  		# Create Play/Pause button		
		self.start = Button(self.master, width=50, padx=3, pady=3, bg='white')
		self.start["text"] = "Play/Pause"
		self.start["command"] = self.playMovie
		self.start.grid(row=2, column=4, padx=2, pady=2)
		startButtonImage = ImageTk.PhotoImage(Image.open("Image/playButton.png").resize((50, 50)))
		self.start.configure(image = startButtonImage)
		self.start.image = startButtonImage

		# Create Forward button		
		self.forward = Button(self.master, width=50, padx=3, pady=3, bg='white')
		self.forward["text"] = "Forward"
		self.forward["command"] = self.forwardMovie
		self.forward.grid(row=2, column=5, padx=2, pady=2)
		forwardButtonImage = ImageTk.PhotoImage(Image.open("Image/forwardButton.png").resize((50, 50)))
		self.forward.configure(image = forwardButtonImage)
		self.forward.image = forwardButtonImage
  
		# Create Teardown button
		self.teardown = Button(self.master, width=50, padx=3, pady=3, bg='white')
		self.teardown["text"] = "Stop"
		self.teardown["command"] =  self.exitClient
		self.teardown.grid(row=2, column=6, padx=4, pady=4)
		stopButtonImage = ImageTk.PhotoImage(Image.open("Image/stopButton.png").resize((50, 50)))
		self.teardown.configure(image = stopButtonImage)
		self.teardown.image = stopButtonImage
	
  
		# Create a label to display the packet loss rate
		self.lTitle = LabelFrame(self.master, height=1, text="Packet loss rate")
		self.lTitle.grid(row=3, column=0, columnspan=3, padx=3, pady=3)
  
		self.lossRateLabel = Label(self.lTitle, height=1, textvariable=self.packetLossRate)
		self.lossRateLabel.grid(row=0, column=0, columnspan=3, padx=3, pady=3)
  
		# Create a label to display the video data rate
		self.vTitle = LabelFrame(self.master, height=1, text="Video data rate")
		self.vTitle.grid(row=3, column=3, columnspan=3,padx=3, pady=3)
  
		self.dataRateLabel = Label(self.vTitle, height=1, textvariable=self.videoDataRate)
		self.dataRateLabel.grid(row=0, column=0, columnspan=3, padx=3, pady=3)
  
  		# Create a label to display the video FPS
		self.vTitle = LabelFrame(self.master, height=30, width=200, text="FPS")
		self.vTitle.grid(row=3, column=6, columnspan=3,padx=3, pady=3)
    
		self.fpsLabel = Label(self.vTitle, height=1, textvariable=self.fps)
		self.fpsLabel.grid(row=0, column=1, padx=2, pady=2)
  

	def setupMovie(self):
		"""Setup button handler."""
	#TODO
		self.teardownAcked = 0
		self.frameNbr = 0
		if (self.state == self.INIT):
			self.sendRtspRequest(self.SETUP)
   
	def describeMovie(self):
		"""Describe button handler."""
		if (self.state != self.INIT):
			self.sendRtspRequest(self.DESCRIBE)
	
	def exitClient(self):
		"""Teardown button handler."""
	#TODO
		if (self.state != self.INIT):
			self.start["command"] = self.playMovie
			startButtonImage = ImageTk.PhotoImage(Image.open("Image/playButton.png").resize((50, 50)))
			self.start.configure(image = startButtonImage)
			self.start.image = startButtonImage
      
			self.sendRtspRequest(self.TEARDOWN)
			if (self.playFlag == 1):
				self.event.set()

	def pauseMovie(self):
		"""Pause button handler."""
	#TODO

		if (self.state == self.PLAYING):
			self.start["command"] = self.playMovie
			startButtonImage = ImageTk.PhotoImage(Image.open("Image/playButton.png").resize((50, 50)))
			self.start.configure(image = startButtonImage)
			self.start.image = startButtonImage
   
			self.sendRtspRequest(self.PAUSE)
			self.event.set()
	
	def playMovie(self):
		"""Play button handler."""
	#TODO	
		self.cachefile = CACHE_FILE_NAME + str(self.sessionId) + CACHE_FILE_EXT
		self.playFlag = 1
  
		if (self.state == self.READY):
			self.start["command"] = self.pauseMovie
			startButtonImage = ImageTk.PhotoImage(Image.open("Image/pauseButton.png").resize((50, 50)))
			self.start.configure(image = startButtonImage)
			self.start.image = startButtonImage
      
			self.event = threading.Event()
			self.event.clear()
			threading.Thread(target=self.listenRtp).start()
			self.sendRtspRequest(self.PLAY)
	
	def backwardMovie(self):
		"""Backward button handler""" 
		if (self.state != self.INIT and self.playFlag == 1):
			self.pauseMovie()
			threading.Thread(target=self.backwardProcess).start()

	def backwardProcess(self):
		"""Backward process"""
		while self.state != self.READY:
			pass
		time.sleep(0.2)
		self.frameNbr -= 20
		if (self.frameNbr < 0):
			self.frameNbr = 0
		self.playMovie()
		print("------------------")
		print("END BACKWARD")
  
	def forwardMovie(self):
		"""Forward button handler"""
		if (self.state != self.INIT and self.playFlag == 1):
			self.pauseMovie()
			threading.Thread(target=self.forwardProcess).start()
   
	def forwardProcess(self):
		"""Forward process"""
		while self.state != self.READY:
			pass
		time.sleep(0.2)
		self.frameNbr += 20
		self.playMovie()
		print("-----------------")
		print("END FORWARD")
   
	def resetMovie(self):
		"""Reset button handler."""  
		if (self.state != self.READY):
			threading.Thread(target=self.autoPlayProcess).start()

	def autoPlayProcess(self):
		if (self.state == self.PLAYING):
			self.exitClient()
   
		while self.state != self.INIT:
			pass
		time.sleep(0.5)
      
		self.setupMovie()
  
		while self.state != self.READY:
			pass
		self.playMovie()
  
		print("------------------")
		print("END AUTOPLAY")
			
	
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
					print("Receive packer number", self.frameNbr)
						
					lostRate = float(self.lostPacket) / (self.lostPacket + self.receivePacket) * 100
					self.packetLossRate.set(str(round(lostRate, 2)) + "%")

					# Calculate the video data rate and fps
					currTime = float(time.time())
					self.totalDataIn1Sec += len(rtpPacket.getPacket())
					self.counter += 1
					
					if (currTime - self.time > 1.0) :		
						dataRate = self.totalDataIn1Sec * 8 / (1024 * (currTime - self.time)) 
						fps = self.counter / (currTime - self.time)
						self.videoDataRate.set(str(round(dataRate, 2)) + "kps")
						self.fps.set(str(round(fps, 2)))
						self.time = currTime
						self.totalDataIn1Sec = 0
						self.counter = 0

			except:
				if self.event.isSet():
					self.totalDataIn1Sec = 0
					self.counter = 0
					break
				if self.teardownAcked == 1:
					self.rtpSocket.close()
					self.teardownAcked = 0
					self.lostPacket = 0
					self.receivePacket = 0
					self.frameNbr = 0
					self.totalDataIn1Sec = 0
					self.counter = 0
					break
 

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
		self.label.configure(image = photo, height=290)
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
			data = 'PLAY ' + self.fileName + ' RTSP/1.0\nCSeq: ' + str(self.rtspSeq) + '\nSession: ' + str(self.sessionId) + '\nStartpoint: ' + str(self.frameNbr)
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
						self.openRtpPort()
						self.state = self.READY
					elif (self.requestSent == self.PLAY):
						print("receive PLAY\n")
						self.state = self.PLAYING
					elif (self.requestSent == self.PAUSE):
						print("receive PAUSE\n")
						self.state = self.READY
					elif (self.requestSent == self.TEARDOWN):
						print("receive TEARDOWN\n")
						self.state = self.INIT
						self.teardownAcked = 1
					elif (self.requestSent == self.DESCRIBE):
						print("receive DESCRIBE\n")
						self.pauseMovie()
						self.annouce(data)
						
		time.sleep(0.5)
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

		folder = "Cache"
		for path in os.listdir(folder):
			fullPath = os.path.join(folder, path)
			if os.path.isfile(fullPath):
				os.remove(fullPath)

		time.sleep(1)
		self.clientSocket.close()
		exit()