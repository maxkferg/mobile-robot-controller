import numpy as np


class VectorBuffer:
	"""
	A buffer of row vectors
	Vectors are appended to the first dimension
	"""

	def __init__(self, size, dtype=float):
		if len(size)==1:
			size = [size,1]
		self.size = size
		self.dtype = dtype
		self.items = np.zeros(size,dtype)


	def add(self,vector):
		"""
		Add a vector to the buffer
		"""
		vector = np.array(vector)
		if vector.shape != self.size[1:]:
			raise ValueError("Expected vector of size {0}. Got {1}".format(self.size[1:],vector.shape))
		self.items = np.roll(self.items, shift=1, axis=0)
		self.items[0,:] = vector


	def clean(self,vector=None):
		"""
		Set all the elements to vector
		"""
		if vector is None:
			self.items = np.zeros(self.size)
		else:
			for i in range(self.size[0]):
				self.items[i,:] = vector


	def to_array(self):
		"""
		Return the buffer as an array
		"""
		return self.items