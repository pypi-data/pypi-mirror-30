from .graphCoreFunctions import createAdjList

def BFS(graph,s,Print=False):
	adj = createAdjList(graph)
	nodes_list = graph.getNodes()

	queue = []
	visited = {}
	for node in range(len(nodes_list)):
		visited[nodes_list[node]] = False

	queue.append(s)
	visited[s] = True


	if Print == True:
		print("The result of BFS is :",end=" ")

	while queue:
		s = queue.pop(0)
		if Print == True:
			print(s,end=" ")
		for i in range(len(adj)):
			if visited[nodes_list[i]] == False:
				queue.append(nodes_list[i])
				visited[nodes_list[i]] = True

	if Print == True:
		print(end='\n')
	else:
		return queue
