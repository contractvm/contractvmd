DAPP = {}
QUERIES = {}
UPDATE = {}
INIT = {}

def dapp (c):
	DAPP [c.__name__] = c
	return c

def query (f):
	QUERIES [f.__name__] = { 'function': f }
	return f

def init (f):
	INIT [f.__name__] = { 'function': f }
	return f


class validateQuery:
	def __init__ (self, of):
		self.of = of

	def __call__ (self, f):
		if not self.of in QUERIES:
			QUERIES [self.of] = {}

		QUERIES [self.of]['validate'] = f
		return f

class validateUpdate:
	def __init__ (self, of):
		self.of = of

	def __call__ (self, f):
		if not self.of in UPDATE:
			UPDATE [self.of] = {}

		UPDATE [self.of]['validate'] = f
		return f

class preUpdate:
	def __init__ (self, of):
		self.of = of

	def __call__ (self, f):
		if not self.of in UPDATE:
			UPDATE [self.of] = {}

		UPDATE [self.of]['pre'] = f
		return f



class update:
	def __init__ (self, method):
		self.method = method

	def __call__ (self, f):
		if not f.__name__ in UPDATE:
			UPDATE [f.__name__] = {}

		UPDATE [f.__name__]['function'] = f
		UPDATE [f.__name__]['method'] = self.method
		return f
