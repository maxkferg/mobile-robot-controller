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
			raise ValueError("Expected vector of size",size[1:])
		self.items = np.roll(self.items, shift=1, axis=0)
		self.items[0,:] = vector


	def clean(self):
		"""
		Set all the elements to zero
		"""
		self.items = np.zeros(self.size, self.dtype)


	def to_array(self):
		"""
		Return the buffer as an array
		"""
		return self.items