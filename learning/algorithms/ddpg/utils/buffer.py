import numpy as np


class VectorBuffer:
	"""
	A buffer of column vectors
	Vectors are appended to the first dimension
	"""

	def __init__(self, size, dtype=float):
		if len(size)==1:
			size = [size,1]
		self.size = size
		self.items = np.zeros(size,dtype)


	def add(self,vector):
		"""
		Add a vector to the buffer
		"""
		if vector.shape!=size[1:]
			raise ValueError("Expected vector of size",size[1:])
		np.roll(self.items, shift=1, axis=0)
		self.items[0,:] = vector


	def to_array(self):
		"""
		Return the buffer as an array
		"""
		return self.items