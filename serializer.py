ClopsAcronyms = [None, "TRU", "FAL", "1UI", "2UI", "4UI", "1SI", "2SI", "4SI", "FLO", "STR", 
	"SW1", "SW2", "SW3", "COP", "PSH", "POP", "MAP", "ARR", "EXT", "PUT", 
	"GET", "EXC", "YEQ", "NEQ", "EQU", "REP", "SER", "DON", "PS1","PO1","PS2","PO2","PS3","PO3"]
Clops = dict(zip(ClopsAcronyms, range(len(ClopsAcronyms))))

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
_PS1 = 29
_PO1 = 30
_PS2 = 31
_PO2 = 32
_PS3 = 33
_PO3 = 34

class CleOptimizedCompiler(object):
	class Preserver(object):
		def __init__(self,dest,preserves=None):
			self.preserves = preserves
			self.dest = dest
		def __enter__(self):
			if self.preserves != None:
				if "R1" in self.preserves:
					self.dest.append( _PS1 )
				if "R2" in self.preserves:
					self.dest.append( _PS2 )
		def __exit__(self, type, vaue, tb):
			if self.preserves != None:
				if "R2" in self.preserves:
					self.dest.append( _PO2 )
				if "R1" in self.preserves:
					self.dest.append( _PO1 )

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
		self.Buffer = bytes[::-1] + self.Buffer
	def read(self):
		return self.Buffer.pop()
	def pop(self):
		return self.Stack.pop()
	def push(self,val):
		self.Stack.append(val)

class CleCpu(object):
	def __init__(self,memory):
		self.Memory = memory
		self.Registers = [None,None,None,None]
		self.Debug = False
	def __repr__(self):
		s = [repr(i)[:15] for i in self.Registers]
		return "Registers: ["+", ".join(s)+"]"
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
			print repr(self)
	def cycle(self,byte):
		if self.Debug:
			print "Stack:", self.Memory.Stack
			print ClopsAcronyms[byte], repr(self)
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

		if byte == _PS1:
			self.Memory.push(self.Registers[1])
			return True
		if byte == _PO1:
			self.Registers[1] = self.Memory.pop()
			return True

		if byte == _PS2:
			self.Memory.push(self.Registers[2])
			return True
		if byte == _PO2:
			self.Registers[2] = self.Memory.pop()
			return True

		if byte == _PS3:
			self.Memory.push(self.Registers[3])
			return True
		if byte == _PO3:
			self.Registers[3] = self.Memory.pop()
			return True


class CleVM(object):
	def __init__(self):
		self.Memory = CleMemory()
		self.Cpu = CleCpu(self.Memory)

obj = {"a":1,"b":[1,2,3]}
obj = {"accounting":[{"firstName":"John","lastName":"Doe","age":23},{"firstName":"Mary","lastName":"Smith","age":32}],"sales":[{"firstName":"Sally","lastName":"Green","age":27},{"firstName":"Jim","lastName":"Galley","age":41}]} 
obj = {"web-app":{"servlet":[{"servlet-name":"cofaxCDS","servlet-class":"org.cofax.cds.CDSServlet","init-param":{"configGlossary:installationAt":"Philadelphia, PA","configGlossary:adminEmail":"ksm@pobox.com","configGlossary:poweredBy":"Cofax","configGlossary:poweredByIcon":"/images/cofax.gif","configGlossary:staticPath":"/content/static","templateProcessorClass":"org.cofax.WysiwygTemplate","templateLoaderClass":"org.cofax.FilesTemplateLoader","templatePath":"templates","templateOverridePath":"","defaultListTemplate":"listTemplate.htm","defaultFileTemplate":"articleTemplate.htm","useJSP":False,"jspListTemplate":"listTemplate.jsp","jspFileTemplate":"articleTemplate.jsp","cachePackageTagsTrack":200,"cachePackageTagsStore":200,"cachePackageTagsRefresh":60,"cacheTemplatesTrack":100,"cacheTemplatesStore":50,"cacheTemplatesRefresh":15,"cachePagesTrack":200,"cachePagesStore":100,"cachePagesRefresh":10,"cachePagesDirtyRead":10,"searchEngineListTemplate":"forSearchEnginesList.htm","searchEngineFileTemplate":"forSearchEngines.htm","searchEngineRobotsDb":"WEB-INF/robots.db","useDataStore":True,"dataStoreClass":"org.cofax.SqlDataStore","redirectionClass":"org.cofax.SqlRedirection","dataStoreName":"cofax","dataStoreDriver":"com.microsoft.jdbc.sqlserver.SQLServerDriver","dataStoreUrl":"jdbc:microsoft:sqlserver://LOCALHOST:1433;DatabaseName=goon","dataStoreUser":"sa","dataStorePassword":"dataStoreTestQuery","dataStoreTestQuery":"SET NOCOUNT ON;select test='test';","dataStoreLogFile":"/usr/local/tomcat/logs/datastore.log","dataStoreInitConns":10,"dataStoreMaxConns":100,"dataStoreConnUsageLimit":100,"dataStoreLogLevel":"debug","maxUrlLength":500}},{"servlet-name":"cofaxEmail","servlet-class":"org.cofax.cds.EmailServlet","init-param":{"mailHost":"mail1","mailHostOverride":"mail2"}},{"servlet-name":"cofaxAdmin","servlet-class":"org.cofax.cds.AdminServlet"},{"servlet-name":"fileServlet","servlet-class":"org.cofax.cds.FileServlet"},{"servlet-name":"cofaxTools","servlet-class":"org.cofax.cms.CofaxToolsServlet","init-param":{"templatePath":"toolstemplates/","log":1,"logLocation":"/usr/local/tomcat/logs/CofaxTools.log","logMaxSize":"","dataLog":1,"dataLogLocation":"/usr/local/tomcat/logs/dataLog.log","dataLogMaxSize":"","removePageCache":"/content/admin/remove?cache=pages&id=","removeTemplateCache":"/content/admin/remove?cache=templates&id=","fileTransferFolder":"/usr/local/tomcat/webapps/content/fileTransferFolder","lookInContext":1,"adminGroupID":4,"betaServer":True}}],"servlet-mapping":{"cofaxCDS":"/","cofaxEmail":"/cofaxutil/aemail/*","cofaxAdmin":"/admin/*","fileServlet":"/static/*","cofaxTools":"/tools/*"},"taglib":{"taglib-uri":"cofax.tld","taglib-location":"/WEB-INF/tlds/cofax.tld"}}}

import time
import microjson

vm = CleVM()
vm.Cpu.Registers[0] = obj
vm.Memory.write([Clops["SER"],Clops["DON"]])

j = time.time()
vm.Cpu.run()
bytes = vm.Cpu.Registers[0]
clvmEncodeTime = time.time()-j


j = time.time()
asjson = microjson.to_json(obj)
jsonEncodeTime = time.time()-j

print "Compiled to:", bytes
print "Executing"

vm.Memory.write(bytes)

j = time.time()
vm.Cpu.run()
clvmDecodeTime = time.time() - j

j = time.time()
microjson.from_json(asjson)
jsonDecodeTime = time.time() - j

print "Registers", vm.Cpu.Registers
print "Stack", vm.Memory.Stack

print vm.Cpu.Registers[0]


print "JSON",len(asjson),"bytes"
print "CLVM",len(bytes),"bytes"

format = "%-10s | %-10s | %-15s | %-15s"
print format % ("Method", "Size (b)", "Encode (ms)", "Decode (ms)")
print format % ("JSON", len(asjson), jsonEncodeTime*1000, jsonDecodeTime*1000)
print format % ("CLVM", len(bytes), clvmEncodeTime*1000, clvmDecodeTime*1000)