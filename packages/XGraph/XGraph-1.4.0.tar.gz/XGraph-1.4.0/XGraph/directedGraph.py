from .node import Node

class directedGraph:
	def __init__(self):
		self.nodes = {}
		self.numOfNodes = 0

	def __iter__(self):
		return iter(self.nodes.values())

	def __addNode(self,node):
		self.numOfNodes += 1
		newNode = Node(node)
		self.nodes[node] = newNode
		return newNode


	def addEdge(self,node,toNode,weight=0):
		if node not in self.nodes:
			self.__addNode(node)
		if toNode not in self.nodes:
			self.__addNode(toNode)

		self.nodes[node].addNeigh(self.nodes[toNode],weight)

	def getNodes(self):
		return list(self.nodes.keys())

	def getLen(self):
		return self.numOfNodes

	def __subCycle(self,node,visited,recursionStack):
		visited[node] = True
		recursionStack[node] = True

		for n in self.nodes[node].getConnectedNodes():
			if visited[n.getNode()] == False:
				if self.__subCycle(n.getNode(),visited,recursionStack) == True:
					return True
			elif recursionStack[n.getNode()] == True:
				return True

		recursionStack[node] = False
		return False


	def isCycle(self):
		nodes = self.getNodes()
		visited = {}
		recursionStack = {}
		for node in range(len(nodes)):
			visited[nodes[node]] = False
			recursionStack[nodes[node]] = False

		for node in self.getNodes():
			if visited[node] == False:
				if self.__subCycle(node,visited,recursionStack) == True:
					return True
		return False