ClopsAcronyms = [None, "TRU", "FAL", "1UI", "2UI", "4UI", "1SI", "2SI", "4SI", "FLO", "STR", "SW1", "SW2", "SW3", "COP", "PSH", "POP", "MAP", "ARR", "EXT", "PUT", "GET", "EXC", "YEQ", "NEQ", "EQU", "REP", "SER", "DON"]
Clops = dict(zip(ClopsAcronyms, range(len(ClopsAcronyms))))

class CleCompiler(object):
	@classmethod
	def Compile(cls, obj, dest):
		"""Create instructions that get obj into R0"""
		if isinstance(obj,int):
			dest.append( Clops["1UI"] )
			dest.append( obj )
			return

		if isinstance(obj,str):
			cls.Compile(len(obj), dest)
			dest.append( Clops["STR"] )
			dest.extend( ord(i) for i in obj )
			return

		if isinstance(obj,dict):
			print "Compiling dictionary", obj
			dest.extend( [Clops["MAP"],Clops["PSH"]] )
			for key, val in obj.items():
				cls.Compile(val, dest) 
				dest.append( Clops["PSH"] )
				cls.Compile(key, dest)
				dest.append( Clops["SW1"] )
				# val is on stack, key is in R1
				dest.extend( [Clops["POP"],Clops["SW2"],Clops["POP"],Clops["SW2"]] )
				dest.extend( [Clops["PUT"],Clops["SW2"],Clops["PSH"]] )
			dest.append( Clops["POP"] )
			return
		if isinstance(obj,list):
			print "Compiling list", obj
			dest.extend( [Clops["1UI"],len(obj),Clops["ARR"],Clops["PSH"]] )
			for item in obj:
				cls.Compile(item, dest)
				dest.extend( [Clops["SW1"],Clops["POP"],Clops["SW1"]] )
				dest.extend( [Clops["EXT"],Clops["SW1"],Clops["PSH"]] )
			dest.append( Clops["POP"] )
			return
		print "Can't compile", obj
		return []

_TRU = 1 
_FAL = 2 
_1UI = 3 
_2UI = 4 
_4UI = 5 
_1SI = 6 
_2SI = 7 
_4SI = 8 
_FLO = 9 
_STR = 10 
_SW1 = 11 
_SW2 = 12 
_SW3 = 13 
_COP = 14 
_PSH = 15 
_POP = 16 
_MAP = 17 
_ARR = 18 
_EXT = 19 
_PUT = 20 
_GET = 21 
_EXC = 22 
_YEQ = 23 
_NEQ = 24 
_EQU = 25 
_REP = 26 
_SER = 27 
_DON = 28 

class CleOptimizedCompiler(object):
	class Preserver(object):
		def __init__(self,dest,preserves=None):
			self.preserves = preserves
			self.dest = dest
		def __enter__(self):
			if self.preserves != None:
				if "R1" in self.preserves:
					self.dest.extend( [_SW1, _PSH] )
				if "R2" in self.preserves:
					self.dest.extend( [_SW2, _PSH] )
		def __exit__(self, type, vaue, tb):
			if self.preserves != None:
				if "R2" in self.preserves and "R1" in self.preserves:
					self.dest.extend( [_SW1, _POP, _SW2, _POP, _SW1] )
				elif "R2" in self.preserves:
					self.dest.extend( [_SW2, _POP, _SW2] )
				elif "R1" in self.preserves:
					self.dest.extend( [_SW1, _POP, _SW1] )

	@classmethod
	def Compile(cls, obj, dest, preserves=None):
		"""Create instructions that get obj into R0"""
		if isinstance(obj,int):
			dest.append( _1UI )
			dest.append( obj )
		elif isinstance(obj,str):
			cls.Compile(len(obj), dest)
			dest.append( _STR )
			dest.extend( ord(i) for i in obj )
		elif isinstance(obj,dict):
			with CleOptimizedCompiler.Preserver(dest, preserves):
				dest.extend( [_MAP, _SW2] )
				for key, val in obj.items():
					cls.Compile(key, dest, preserves=set(("R2")))
					dest.append( _SW1 )
					cls.Compile(val, dest, preserves=set(("R2","R1"))) 
					dest.append( _PUT )
				dest.append(_SW2)
		elif isinstance(obj,list):
			with CleOptimizedCompiler.Preserver(dest, preserves):
				dest.extend( [_1UI,len(obj),_ARR, _SW1] )

				for item in obj:
					cls.Compile(item, dest, preserves=set(["R1"]))
					dest.append( _EXT )
				dest.append(_SW1)
		else:
			raise Exception("Can't compile "+str(obj))



class CleMemory(object):
	def __init__(self):
		self.Buffer = []
		self.Stack = []
	def write(self,bytes):
		self.Buffer.extend(bytes)
	def read(self):
		return self.Buffer.pop(0)
	def pop(self):
		return self.Stack.pop()
	def push(self,val):
		self.Stack.append(val)

class CleCpu(object):
	def __init__(self,memory):
		self.Memory = memory
		self.Registers = [None,None,None,None]
		self.Debug = False
	def run(self):
		try:
			print "CPU running: ",
			while True:
				byte = self.Memory.read()
				if self.cycle(byte):
					continue
				break
			print "Done"
		except Exception, e:
			print ""
			print "SEGFAULT:", e
			print "Stack:", self.Memory.Stack
			print "Registers:", self.Registers
	def cycle(self,byte):
		if self.Debug:
			print ClopsAcronyms[byte],
			print "Registers:", self.Registers
			print "Stack:", self.Memory.Stack
		if byte == _SER:
			dest = []
			CleOptimizedCompiler.Compile(self.Registers[0], dest)
			dest.append(_DON)
			self.Registers[0] = dest
			return True
		if byte == _DON:
			return False
		if byte == _TRU:
			self.Registers[0] = True
			return True
		if byte == _FAL:
			self.Registers[0] = False
			return True
		if byte == _1UI:
			self.Registers[0] = self.Memory.read()
			return True
		if byte == _2UI:
			return True
		if byte == _4UI:
			return True
		if byte == _1SI:
			return True
		if byte == _2SI:
			return True
		if byte == _4SI:
			return True
		if byte == _FLO:
			return True
		if byte == _STR:
			s = ""
			for i in range(self.Registers[0]):
				s += chr(self.Memory.read())
			self.Registers[0] = s
			return True
		if byte == _SW1:
			self.Registers[0], self.Registers[1] = self.Registers[1], self.Registers[0]
			return True
		if byte == _SW2:
			self.Registers[0], self.Registers[2] = self.Registers[2], self.Registers[0]
			return True
		if byte == _SW3:
			self.Registers[0], self.Registers[3] = self.Registers[3], self.Registers[0]
			return True
		if byte == _COP:
			return True
		if byte == _PSH:
			self.Memory.push(self.Registers[0])
			return True
		if byte == _POP:
			self.Registers[0] = self.Memory.pop()
			return True
		if byte == _MAP:
			self.Registers[0] = {}
			return True
		if byte == _ARR:
			self.Registers[0] = []
			return True
		if byte == _EXT:
			self.Registers[1].append(self.Registers[0])
			return True
		if byte == _PUT:
			self.Registers[2][self.Registers[1]]=self.Registers[0]
			return True
		if byte == _GET:
			key = self.Registers[1]
			if key in self.Registers[2]:
				self.Registers[0] = self.Registers[2][key]
				self.Registers[1] = True
			else:
				self.Registers[1] = False
			return True
		if byte == _EXC:
			return True
		if byte == _YEQ:
			return True
		if byte == _NEQ:
			return True
		if byte == _EQU:
			return True
		if byte == _REP:
			times = self.Registers[1]
			ops = [self.Memory.read() for i in range(times)]
			self.Registers[0] = self.Registers[2]
			self.Registers[1] = self.Registers[3]
			while times > 0:
				times -= 1
				for op in ops:
					if not self.cycle(op):
						return False
			return True


class CleVM(object):
	def __init__(self):
		self.Memory = CleMemory()
		self.Cpu = CleCpu(self.Memory)

obj = {"a":1,"b":[1,2,3]}
obj = {"accounting":[{"firstName":"John","lastName":"Doe","age":23},{"firstName":"Mary","lastName":"Smith","age":32}],"sales":[{"firstName":"Sally","lastName":"Green","age":27},{"firstName":"Jim","lastName":"Galley","age":41}]} 

import time
import microjson

vm = CleVM()
vm.Cpu.Registers[0] = obj
vm.Memory.write([Clops["SER"],Clops["DON"]])

j = time.time()
vm.Cpu.run()
print "Clevm encoded in", (time.time()-j)*1000, "ms"

j = time.time()
asjson = microjson.to_json(obj)
print "Json encoded in", (time.time()-j)*1000, "ms"

bytes = vm.Cpu.Registers[0]

print "Compiled to:", bytes
print "That's",len(bytes),"bytes"
print "Executing"

vm.Memory.write(bytes)

j = time.time()
vm.Cpu.run()

print ""
print "Clevm took", (time.time()-j)*1000, "ms"

j = time.time()
microjson.from_json(asjson)
print "Json took", (time.time()-j)*1000, "ms"

print "Registers", vm.Cpu.Registers
print "Stack", vm.Memory.Stack

print vm.Cpu.Registers[0]