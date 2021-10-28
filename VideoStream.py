class VideoStream:
	def __init__(self, filename):
		self.filename = filename
		try:
			self.file = open(filename, 'rb')
		except:
			raise IOError
		self.frameNum = 0
		self.totalFrame = 0
		self.frameArr = [0]
		self.calc()
 
	def calc(self):
		"""Get number of total frame"""
		self.tmpFile = open(self.filename, 'rb')
		while True:
			data = self.tmpFile.read(5)
			if data: 
				framelength = int(data)
								
				# Read the current frame
				data = self.tmpFile.read(framelength)
				self.totalFrame += 1
				self.frameArr.append(self.frameArr[-1] + 5 + framelength)
			else:
				break

	# def sendFrame(self, ith):
	# 	"""Send frame ith"""
	# 	self.tmpFile = open(self.filename, 'rb')
	# 	self.tmpFile.read(self.frameArr[ith])
	# 	data = self.tmpFile.read(5) # Get the framelength from the first 5 bits
	# 	if data: 
	# 		framelength = int(data)
							
	# 		# Read the current frame
	# 		data = self.tmpFile.read(framelength)
	# 	return data
 
	def setFramePoint(self, ith):
		"""Set start frame point"""
		self.file.close()
		self.file = open(self.filename, 'rb')
		self.file.read(self.frameArr[ith])
		self.frameNum = ith
   
	def nextFrame(self):
		"""Get next frame."""
		data = self.file.read(5) # Get the framelength from the first 5 bits
		if data: 
			framelength = int(data)
							
			# Read the current frame
			data = self.file.read(framelength)
			self.frameNum += 1
		return data
		
	def frameNbr(self):
		"""Get frame number."""
		return self.frameNum
	
	