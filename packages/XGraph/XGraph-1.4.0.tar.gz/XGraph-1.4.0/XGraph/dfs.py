'''
###############################################################
 Dfs Algorithm returns a list of form (Node,Pos) where the Node
 is the name of the node and
 Pos is the number of node discovery position.
 Nodes now can be strings.
 ##############################################################
'''

from .graphCoreFunctions import createAdjList, getNeigh

discoverPos = 0


def dfsSub(graph,node,visited,stack):

	global discoverPos

	visited[node] = True
	discoverPos +=1 
	stack.append([node,discoverPos])

	for n in getNeigh(graph,node):
		if visited[n] == False: 
			dfsSub(graph,n,visited,stack)


def DFS(graph,start,Print=False):
	stack = []
	# Better Optimization Needed(Not Tested!)
	# -----------------------------------------------
	# Here we initialize the "visited" dict that shows which node is visited .
	nodes = graph.getNodes()
	visited = {}
	# Here we init all nodes with False value.
	# That means that in the start none of the node is visited!
	for node in range(len(nodes)):
		visited[nodes[node]] = False
	# -----------------------------------------------
	dfsSub(graph,start,visited,stack) 

	if Print == False:
		return stack
	else:
		print("The result(Node,Pos) of DFS is :",' '.join([str(n) for n in stack]),end='\n')

