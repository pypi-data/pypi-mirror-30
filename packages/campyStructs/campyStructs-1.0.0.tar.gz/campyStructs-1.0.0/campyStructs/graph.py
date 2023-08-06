class Node:
    def __init__(self,id):
        self.id = id
        self.neighbors = {}

    def getid(self):
        return self.id

    def getneighbors(self):
        return self.neighbors.keys()

    def addneighbor(self, neighbor, weight):
        self.neighbors[neighbor] = weight

    def getweight(self, neighbor):
        return self.neighbors.get(neighbor)

class Graph:
    def __init__(self):
        self.numnodes = 0
        self.nodelist = {}

    def addnode(self,id):
        self.numnodes = self.numnodes+1
        newnode = Node(id)
        self.nodelist[id] = newnode
        return newnode

    def addedge(self, to, frm, weight):
        if to not in self.nodelist:
            addnode(to)
        if frm not in self.nodelist:
            addnode(frm)
        self.nodelist.get(to).addneighbor(self.nodelist[frm], weight)

    def listnodes(self):
        return self.nodelist.keys()

    def getnode(self, id):
        return self.nodelist.get(id)

