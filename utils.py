from shapely.geometry import LineString
from shapely import wkt

class PriorityQueue:
    def __init__(self):
        self.elements = []
    
    def BubbleSortQueue(self,items):
        for i in range(len(items)):
            for k in range(len(items)-1):
                if float(items[k][1]) > float(items[k+1][1]):
                    temp = items[k]
                    items[k] = items[k+1]
                    items[k+1] = temp
        
        return items
    
    def IsEmpty(self):
        if len(self.elements) == 0:
            return True
    
    def Enqueue(self, item):
        self.elements.append(item)
        self.BubbleSortQueue(self.elements)
    
    def Dequeue(self):
        if self.IsEmpty():
            raise IndexError("Pop from an empty queue")
        
        return self.elements.pop(0)
    
class Stack:
    # Top of the stack is the last index of the list
    def __init__(self):
        self.elements = []
    
    def Push(self, item):
        self.elements.append(item)
    
    def Pop(self):
        if not self.isEmpty():
            return self.elements.pop()
        else:
            raise IndexError("Pop from an empty stack")
    
    def Peek(self):
        if not self.isEmpty():
            return self.elements[-1]
        else:
            raise IndexError("Peek from an empty stack")

    def isEmpty(self):
        return len(self.elements) == 0
    
    def size(self):
        return len(self.elements)

def RescaleNodes(nodes, edges, width, height, padding_x = 0, padding_y = 0):
    max_x = -float('inf')
    min_x = float('inf')
    max_y = -float('inf')
    min_y = float('inf')
    
    # Get minimum and maximum x and y values
    for node in nodes:
        x, y = float(node["data"]["x"]), float(node["data"]["y"])
        if x > max_x:
            max_x = float(node["data"]["x"])
        if x < min_x:
            min_x = float(node["data"]["x"])
        if y > max_y:
            max_y = float(node["data"]["y"])
        if y < min_y:
            min_y = float(node["data"]["y"])
                        
    # Scale positions to fit defined space
    scaledNodes = []
    for node in nodes:
        scaled_x = (float(node["data"]["x"]) - min_x) / (max_x - min_x) * (width) + padding_x
        scaled_y = height - (float(node["data"]["y"]) - min_y) / (max_y - min_y) * (height) + padding_y

        scaledNode = node
        scaledNode["data"]["x"] = scaled_x
        scaledNode["data"]["y"] = scaled_y
        scaledNodes.append(scaledNode)
    
    for edge in edges:
        if 'geometry' in edge['data']:
            points = list(wkt.loads(edge['data']['geometry']).coords)
            scaledPoints = []
            for point in points:
                scaledPoint_x = (point[0] - min_x) / (max_x - min_x) * (width) + padding_x
                scaledPoint_y = height - (point[1] - min_y) / (max_y - min_y) * (height) + padding_y

                scaledPoint = (scaledPoint_x,scaledPoint_y)
                scaledPoints.append(scaledPoint)
            scaledPointsLineString = LineString(scaledPoints)
            edge['data']['geometry'] = scaledPointsLineString.wkt
    
    return scaledNodes

    