class NodeS:
    def __init__(self,value):
        self.value = value
        self.next = None

class NodeD:
    def __init__(self,value):
        self.value = value
        self.next = None
        self.previous = None

class singleLL:
    def __init__(self):
        self.head = None

    def addNode(self, value):
        newNode = NodeS(value)
        if self.head == None:
            self.head = newNode
        else:
            newNode.next = self.head
            self.head = newNode

    def addNodeEnd(self, value):
        newNode = NodeS(value)
        current = self.head
        while current.next != None:
            current = current.next
        current.next = newNode

    def search(self, value):
        if self.head == None:
            return False
        current = self.head
        while currrent.next != None:
            if current.value == value:
                return current
            current = current.next

class doubleLL:
    def __init__(self):
        self.head = None

    def addNode(self, value):
        newNode = NodeD(value)
        if self.head == None:
            self.head = newNode
        else:
            newNode.next = self.head
            self.head = newNode

    def addNodeEnd(self, value):
        newNode = NodeD(value)
        current = self.head
        while current.next != None:
            current = current.next
        current.next = newNode
        newNode.previous = current

    def search(self, value):
        if self.head == None:
            return False
        current = self.head
        while currrent.next != None:
            if current.value == value:
                return current
            current = current.next

