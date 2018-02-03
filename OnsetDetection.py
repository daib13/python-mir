import numpy as np
from scipy.fftpack import fft

class OnsetDetection(object):
	"""
	Onset Detection Algorithm that finds the onset times of an audio file. There are three types
	of onset detection algorithms which are : 1) Spectral Flux, 2) High Frequency Content and 3) Complex Domain

	Attributes:
	inputSignal: The audio file
	fs: Sampling rate
	detectionType: The algorithm to calculate the onset detection function
	hopTime: Length of overlapping window in seconds
	fftTime: Length of FFT size in seconds
	detectionFunc: The output of the onset detection function

	"""

	def __init__(self, inputSignal, fs = 44100, hopTime = 0.01, fftTime = 0.04, detectionType = "Complex Domain"):
		self.inputSignal = inputSignal
		self.fs = fs
		self.hopTime = hopTime
		self.fftTime = fftTime
		self.hopSize = round(fs * hopTime)
		self.fftOrder = np.ceil(np.log2(self.fs * self.fftTime))
		self.fftSize = int(pow(2, self.fftOrder))

		self.frameCount = int(np.floor((len(self.inputSignal) - self.fftSize) / self.hopSize))
		self.currentFrameFFT = np.zeros(self.fftSize)
		self.prevFrameFFT = np.zeros(self.fftSize)
		self.prevPrevFrameFFT = np.zeros(self.fftSize)
		self.detectionFunc = np.zeros(self.frameCount)

		self.detectionType = detectionType


	def spectralFlux(self):
		result = 0

		for i in range(self.fftSize):
			currentMag = np.abs(self.currentFrameFFT[i])
			prevMag = np.abs(self.prevFrameFFT[i])
			if (currentMag > prevMag):
				result += currentMag - prevMag

		result /= self.fftSize
		return result

	def highFrequencyContent(self):
		result = 0

		for i in range(self.fftSize):
			currentMag = np.abs(self.currentFrameFFT[i])

			if (i <= self.fftSize/2):
				result += pow(currentMag, 2) * i
			else:
				result += pow(currentMag, 2) * (self.fftSize - i)

		result /= self.fftSize
		return result

	def complexDomain(self):
		result = 0

		for i in range(self.fftSize):
			currentMag = np.abs(self.currentFrameFFT[i])
			prevMag = np.abs(self.prevFrameFFT[i])
			currentPhase = np.angle(self.currentFrameFFT[i])
			prevPhase = np.angle(self.prevFrameFFT[i])
			prevPrevPhase = np.angle(self.prevPrevFrameFFT[i])
			targetPhase = 2 * prevPhase - prevPrevPhase
			result += np.sqrt(pow(prevMag, 2) + pow(currentMag, 2) - 2 * prevMag * currentMag * np.cos(currentPhase - targetPhase))

		result /= self.fftSize
		return result

	def process(self):

		for i in range(self.frameCount):
			ptr = i * self.hopSize
			currentFrame = self.inputSignal[ptr:ptr + self.fftSize] # get current frame
			currentFrame = currentFrame * np.hamming(self.fftSize) # apply hamming window
			currentFrame = np.append(currentFrame, np.zeros(self.fftSize)) # zero pad
			self.currentFrameFFT = fft(currentFrame, self.fftSize)

			if (self.detectionType == "Complex Domain"):
				self.detectionFunc[i] = self.complexDomain()
			elif (self.detectionType == "spectralFlux"):
				self.detectionType[i] = self.spectralFlux()
				
			self.prevPrevFrameFFT = self.prevFrameFFT
			self.prevFrameFFT = self.currentFrameFFT

		return self.detectionFunc