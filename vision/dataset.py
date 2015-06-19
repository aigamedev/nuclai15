import random
import itertools

import numpy
import scipy


class Dataset(object):

	def __init__(self, width=63, height=63):
		self.filenames = []
		self.data = []
		self.width = width
		self.height = height
	
	def store(self, files, result, times=1):
		for f in itertools.chain(*[files for _ in range(times)]):
			i = len(self.filenames)
			img = scipy.misc.imread(f) / 255.0 - 0.5
	
			if times > 1:
				# Randomly flip in the X direction.
				if random.random() > 0.5:
					img = img[:,::-1]
	
			self.filenames.append(f)
			self.data.append((img, result))

	def toarray(self):
		N = len(self.filenames)
		X = numpy.zeros((N, self.width, self.height, 3), dtype=numpy.float32)
		y = numpy.zeros((N, 1), dtype=numpy.int32)
		
		for index, (img, result) in enumerate(self.data):
			X[index] = img
			y[index] = result

		return X, y
