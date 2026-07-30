import networkx as nx
import pygame
import math
from shapely.geometry import LineString
from shapely import wkt
import utils
import ui
import time
import os

# Load pygame
pygame.init()
screen = pygame.display.set_mode((1280,720))
pygame.display.set_caption('Pathfinding Learning Tool NEA')
clock = pygame.time.Clock()
running = True

# Initialise UI

# Initialise color scheme
VERYDARK = (34, 40, 49)
DARK = (57, 62, 70)
LIGHT = (238, 238, 238)
BLUE = (0, 173, 181)
GREEN = (56, 118, 29)

# Initialise fonts
fontLexendLarge = pygame.font.SysFont("fonts\Lexend\Lexend-VariableFont_wght.ttf", 44)
fontLexendSmall = pygame.font.SysFont("fonts\Lexend\Lexend-VariableFont_wght.ttf", 32)
fontRobotoMonoLarge = pygame.font.Font("fonts\Roboto_Mono\RobotoMono-VariableFont_wght.ttf", 16)
fontRobotoMonoSmall = pygame.font.Font("fonts\Roboto_Mono\RobotoMono-VariableFont_wght.ttf", 13)

#regions
navbarRegion = ui.NavbarRegion("Navbar", (0,0), (1280,90), "Pathfinding Learning Toolkit", (30,30))
pathfindingRegion = ui.PathfindingRegion("Pathfinding Region", (10,100), (850,610))
pathfindingNodePadding = 30
buttonRegion = ui.ButtonRegion("Button Region", (870,100), (400,300), None)
consoleRegion = ui.ConsoleRegion("Console Region", (870,410), (400,300))

#buttons
startButton = ui.StartButton("Start", (10,10), (185,62.5), buttonRegion, True)
resetButton = ui.ResetButton("Reset", (10,77.5), (185,62.5), buttonRegion, True)
pathfindingTypeButton = ui.ChangePathfindingButton("Search Type", (10,160), (185,62.5), buttonRegion, True)
changeConsoleButton = ui.ChangeConsoleButton("Change Console", (10,227.5), (185,62.5), buttonRegion, True)
nextMapButton = ui.NextMapButton("Next Map", (205,10), (185,62.5), buttonRegion, True, ["littlehampton","worthing","manhattan"])
pauseButton = ui.PauseButton("Pause", (205,92.5), (185,62.5), buttonRegion, True)
resumeButton = ui.ResetButton("Resume", (205,160), (185,62.5), buttonRegion, True)
nextStepButton = ui.NextStepButton("Next Step", (205,227.5), (185,62.5), buttonRegion, True)

buttons = [startButton,resetButton,pathfindingTypeButton,changeConsoleButton,nextMapButton,pauseButton,resumeButton,nextStepButton]
startNode = ""
endNode = ""
activelyPathfinding = False
pathfinding = False
foundEnd = False
visited = []
path = []
currentNodeChanging = 0
timeTaken = 0
timeStarted = 0
timeEnded = 0
pathfindingType = 0
consoleLog = []

currentLineIndex = 0

consoleMode = 0

currentPathfindingText = "Depth-First"

# Each item is a seperate line
consoleFileLog = []

def LoadGraph():
    # Load the graph file
    currentMap = nextMapButton.GetCurrentMap()
    Graph = nx.read_graphml('./data/'+currentMap+'.graphml')

    # List to store nodes
    nodes = []
    for node, data in Graph.nodes(data=True):
        nodes.append({
            'node_id': node,
            'data': data
        })

    # List to store edges with their attributes
    edges = []
    for u, v, data in Graph.edges(data=True):
        edges.append({
            'source': u,    # Start node of the edge
            'target': v,    # End node of the edge
            'data': data    # Edge attributes (e.g., weight, length)
        })
    
    # Get nodes and rescale their positions to fit onto the screen
     
    scaledNodes = utils.RescaleNodes(nodes,edges,pathfindingRegion.GetSize()[0]-pathfindingNodePadding,pathfindingRegion.GetSize()[1]-pathfindingNodePadding,pathfindingRegion.GetPosition()[0]+pathfindingNodePadding/2,pathfindingRegion.GetPosition()[1]+pathfindingNodePadding/2)
    
    return Graph, nodes, scaledNodes, edges

def DrawText(text,font,textColour,position):
    img = font.render(text, True, textColour)
    screen.blit(img,position)

def PrintToConsole(text,position,textColour,mode = 0):
    if mode == 1:
        img = fontRobotoMonoSmall.render(text, True, textColour)
    else:
        img = fontRobotoMonoSmall.render("> "+text, True, textColour)
    screen.blit(img,(consoleRegion.GetPosition()[0]+5,consoleRegion.GetPosition()[1]+5+15*position))

def AppendConsoleLog(text,textColour="green"):
    global consoleLog
    global consoleFileLog
    
    t = time.localtime()
    consoleFileLog.append(str(time.strftime("%H:%M:%S", t)) + " -> " + text)
    if len(consoleLog) < 19:
        consoleLog.append((text,textColour))
    else:
        consoleLog.append((text,textColour))
        consoleLog = consoleLog[len(consoleLog)-19:len(consoleLog)]
    
    if text[0:12] == "Search type:":
        UpdateFrame()

def UpdateLiveConsole(node,line):
    if consoleMode == 0:
        UpdateFrame(node,line)

def DrawUI(line):
    # Draw navbar
    rect = pygame.Rect(navbarRegion.GetPosition()[0],navbarRegion.GetPosition()[1],navbarRegion.GetSize()[0],navbarRegion.GetSize()[1])
    pygame.draw.rect(screen,VERYDARK,rect)
    textPosition = (navbarRegion.GetPosition()[0] + navbarRegion.GetNavbarTextPadding()[0],navbarRegion.GetPosition()[1] + navbarRegion.GetNavbarTextPadding()[1])
    DrawText(navbarRegion.GetNavbarText(),fontLexendLarge,LIGHT,textPosition)
    
    # Draw pathfinding area
    rect = pygame.Rect(pathfindingRegion.GetPosition()[0],pathfindingRegion.GetPosition()[1],pathfindingRegion.GetSize()[0],pathfindingRegion.GetSize()[1])
    pygame.draw.rect(screen,VERYDARK,rect)
    
    # Draw button area
    rect = pygame.Rect(buttonRegion.GetPosition()[0],buttonRegion.GetPosition()[1],buttonRegion.GetSize()[0],buttonRegion.GetSize()[1])
    pygame.draw.rect(screen,VERYDARK,rect)
    
    # Draw console area
    rect = pygame.Rect(consoleRegion.GetPosition()[0],consoleRegion.GetPosition()[1],consoleRegion.GetSize()[0],consoleRegion.GetSize()[1])
    pygame.draw.rect(screen,VERYDARK,rect)
    
    # Draw information text
    DrawText("Current Map: "+nextMapButton.GetCurrentMap().capitalize(),fontLexendSmall,LIGHT,(525,35))
    DrawText("Current Pathfinding Type: "+currentPathfindingText,fontLexendSmall,LIGHT,(860,35))

#     CONSOLE MODE 1 - LOG
    if len(consoleLog) > 0 and consoleMode == 1:
        if len(consoleLog) < 19:
            for i in range(len(consoleLog)):
                PrintToConsole(consoleLog[i][0],i,consoleLog[i][1])
        else:
            for i in range(19):
                PrintToConsole(consoleLog[i][0],i,consoleLog[i][1])

#     CONSOLE MODE 2 - PSEUDO
    elif pathfindingType == 0 and consoleMode == 0:
        lines = []
        file = open("depthfirst.txt","r")
        lines = file.read().split("\n")
        file.close()
        for i in range(len(lines)):
            if i == line:
                PrintToConsole(lines[i],i,GREEN,1)
            else:
                PrintToConsole(lines[i],i,LIGHT,1)
                
    elif pathfindingType == 1 and consoleMode == 0:
        lines = []
        file = open("dijkstras.txt","r")
        lines = file.read().split("\n")
        file.close()
        for i in range(len(lines)):
            if i == line:
                PrintToConsole(lines[i],i,GREEN,1)
            else:
                PrintToConsole(lines[i],i,LIGHT,1)
        
    elif pathfindingType == 2 and consoleMode == 0:
        lines = []
        file = open("astar.txt","r")
        lines = file.read().split("\n")
        file.close()
        for i in range(len(lines)):
            if i == line:
                PrintToConsole(lines[i],i,GREEN,1)
            else:
                PrintToConsole(lines[i],i,LIGHT,1)
           
    # Draw buttons
    for button in buttons:
        rect = pygame.Rect(button.GetInheritedPosition()[0],button.GetInheritedPosition()[1],button.GetSize()[0],button.GetSize()[1])
        pygame.draw.rect(screen,DARK,rect)
        textPosition = (button.GetButtonTextPosition(fontLexendSmall)[0],button.GetButtonTextPosition(fontLexendSmall)[1])
        DrawText(button.GetName(),fontLexendSmall,LIGHT,textPosition)

def DrawGraph(currentNode):
    # Draw the edges
    for edge in edges:
        # If it isnt a straight line it will have geometry property
        if edge['source'] in path and edge['target'] in path:
            color = "green"
        elif edge['source'] in visited and edge['target'] in visited:
            color = "yellow"
        else:
            color = LIGHT
        if 'geometry' in edge['data']:
            points = list(wkt.loads(edge['data']['geometry']).coords)
            for i in range(len(points)-1):
                pygame.draw.line(screen, color, (points[i][0],points[i][1]), (points[i+1][0],points[i+1][1]), 1)
        # Straight line, just draw from source and end node
        else:
            # Find the source node position
            sourceNode = None
            for node in scaledNodes:
                if node["node_id"] == edge["source"]:
                    sourceNode = node
                    break

            # Find the target node position
            targetNode = None
            for node in scaledNodes:
                if node["node_id"] == edge["target"]:
                    targetNode = node
                    break

            # Get the positions of source and target nodes
            if sourceNode and targetNode:
                sourcePos = (float(sourceNode["data"]["x"]), float(sourceNode["data"]["y"]))
                targetPos = (float(targetNode["data"]["x"]), float(targetNode["data"]["y"]))

                # Draw a line between the source and target using aalines
                pygame.draw.line(screen, color, sourcePos, targetPos, 1)
    # Draw the graph
    for node in scaledNodes:
        if node['node_id'] == startNode:
            pygame.draw.circle(screen, "green", (float(node["data"]["x"]), float(node["data"]["y"])), 4)
        elif node['node_id'] == endNode:
            pygame.draw.circle(screen, "red", (float(node["data"]["x"]), float(node["data"]["y"])), 4)
        elif node['node_id'] in path:
            pygame.draw.circle(screen, "green", (float(node["data"]["x"]), float(node["data"]["y"])), 3)
        elif node['node_id'] == currentNode:
            pygame.draw.circle(screen, "purple", (float(node["data"]["x"]), float(node["data"]["y"])), 3)
    

# Heuristic function for getting hCost
def Heuristic(nodeA, nodeB):
    nodeA_data = None
    nodeB_data = None
    for node in scaledNodes:
        if node['node_id'] == nodeA:
            nodeA_data = node
        if node['node_id'] == nodeB:
            nodeB_data = node
    if nodeA_data and nodeB_data:
        x1, y1 = float(nodeA_data['data']['x']), float(nodeA_data['data']['y'])
        x2, y2 = float(nodeB_data['data']['x']), float(nodeB_data['data']['y'])
        return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return float('inf')  # Return a high cost if nodes are not found

def GetNodeNeighbors(node):
    # Use the node ID to match up with edges which start at this node
    # Use the edge's target ID to get the neighboring nodes
    neighbors = []
    for edge in edges:
        if node == edge['source']:
            neighbors.append((edge['target'],edge['data']['length']))
    return neighbors

def DepthFirstStep():
    # Update the psuedocode console view to the appropriate line
    # Each time this subroutine is called and the current console mode is psuedocode mode, the frame updates
    UpdateLiveConsole(None,1)
    
    # Pop node off of the stack
    currentNode = dfsStack.Pop()
    
    AppendConsoleLog("Visiting the next node in the stack")
    
    UpdateLiveConsole(currentNode,3)
    
    # Has the node already been visited
    if currentNode in visited:
        AppendConsoleLog("Node already visited!","red")
        return True
    
    UpdateLiveConsole(currentNode,4)
    # Add this node to the visited list
    visited.append(currentNode)
    AppendConsoleLog("Added this node to the visited nodes list")
    
    # If the console mode is the log mode update frame
    if consoleMode == 1:
        UpdateFrame(currentNode)
    
    UpdateLiveConsole(currentNode,7)
    # Is this the end node
    if currentNode == endNode:
        AppendConsoleLog("Found End With Depth First","red")
        timeEnded = time.time()
        # Get the time it took to find the end
        timeTaken = timeEnded - timeStarted
        AppendConsoleLog("Time taken: "+str(round(timeTaken,1))+"s","red")
        AppendConsoleLog("Nodes searched: "+str(len(visited)),"red")
        global foundEnd
        foundEnd = True
        UpdateLiveConsole(currentNode,8)
        for node in visited:
            path.append(node)
        UpdateFrame()
        UpdateLiveConsole(currentNode,9)
        return False
    
    UpdateLiveConsole(currentNode,11)
    # Get the neighbors of the current node
    neighbors = GetNodeNeighbors(currentNode)
    AppendConsoleLog("This node has "+str(len(neighbors))+" neighbors!")
    AppendConsoleLog("Pushing these nodes onto the stack...")
    UpdateLiveConsole(currentNode,12)
    # Loop through each neighbor
    # If the neighbor isnt already in the stack, push it onto the stack
    for neighbor in neighbors:
        UpdateLiveConsole(currentNode,13)
        if neighbor not in visited and neighbor not in dfsStack.elements:
            UpdateLiveConsole(currentNode,15)
            dfsStack.Push(neighbor[0])
            
    UpdateLiveConsole(currentNode,18)
    return True

def DijkstraStep():
    # Update the psuedocode console view to the appropriate line
    # Each time this subroutine is called and the current console mode is psuedocode mode, the frame updates
    UpdateLiveConsole(None,1)
    
    # Dequeue from the priority queue to get current node
    currentNode, currentDistance = priorityQueue.Dequeue()
    currentNodeID = currentNode
    
    AppendConsoleLog("Visiting the closest node to the start node")
    AppendConsoleLog("It is: "+str(round(currentDistance,1))+" meters away from the start node")
    
    # If the console mode is the log mode update frame
    if consoleMode == 1:
        UpdateFrame(currentNode)
        
    # Skip this node if already visited - Dijkstra never searches a node more than once
    UpdateLiveConsole(currentNode,3)
    if currentNode in visited:
        AppendConsoleLog("Node already visited!","red")
        return True
    
    UpdateLiveConsole(currentNode,4)
    # Add this node to the visited list
    visited.append(currentNode)
    AppendConsoleLog("Added this node to the visited nodes list")    
    
    UpdateLiveConsole(currentNode,6)
    # Is this the end node
    if currentNode == endNode:
        # Visited the end node so exit the loop entirely
        AppendConsoleLog("Found End With Dijkstras","red")
        timeEnded = time.time()
        timeTaken = timeEnded - timeStarted
        # Get the time taken to find the end node
        AppendConsoleLog("Time taken: "+str(round(timeTaken,1))+"s","red")
        AppendConsoleLog("Nodes searched: "+str(len(visited)),"red")
        RetracePath(currentNode)
        global foundEnd
        UpdateLiveConsole(currentNode,7)
        foundEnd = True
        UpdateFrame()
        UpdateLiveConsole(currentNode,8)
        return False
        
    # Examine the neighbors (connected nodes)
    UpdateLiveConsole(currentNode,10)
    neighbors = GetNodeNeighbors(currentNode)
    AppendConsoleLog("This node has "+str(len(neighbors))+" neighbors!")
    AppendConsoleLog("Calculating the distance of the start node to")
    AppendConsoleLog("each neighbor...")
    UpdateLiveConsole(currentNode,11)
    for neighbor in neighbors:
        neighborNode = neighbor[0]
        edgeLength = neighbor[1]

        # Calculate the distance to this neighbor from the start node via this node
        UpdateLiveConsole(currentNode,12)
        newDistance = float(currentDistance) + float(edgeLength)

        # If a shorter distance to the neighbor is found, update the shortest distance
        UpdateLiveConsole(currentNode,13)
        if newDistance < distances[neighborNode]:
            UpdateLiveConsole(currentNode,14)
            distances[neighborNode] = newDistance
            UpdateLiveConsole(currentNode,15)
            parent[neighborNode] = currentNode
            
            UpdateLiveConsole(currentNode,16)
            # Push the updated distance to the priority queue
            priorityQueue.Enqueue((neighborNode,newDistance))        
    
    UpdateLiveConsole(currentNode,18)
    return True

def AStarStep():
    # Update the psuedocode console view to the appropriate line
    # Each time this subroutine is called and the current console mode is psuedocode mode, the frame updates
    UpdateLiveConsole(None,1)
    
    # Pop the node in front of the queue (smallest f-score)
    currentNode, currentFScore = priorityQueue.Dequeue()
    currentNodeID = currentNode
    
    AppendConsoleLog("Visiting the node that has the lowest f-score")
    AppendConsoleLog("This nodes f-score is "+str(currentFScore))
    
    # Skip this node if already visited
    UpdateLiveConsole(currentNode,2)
    if currentNode in visited:
        AppendConsoleLog("Node already visited!","red")
        return True
    
    # If the console mode is the log mode update frame
    if consoleMode == 1:
        UpdateFrame(currentNode)
    
    UpdateLiveConsole(currentNode,3)
    # Add this node to the visited list
    visited.append(currentNode)
    AppendConsoleLog("Added this node to the visited nodes list")
    UpdateFrame(currentNode)
    
    UpdateLiveConsole(currentNode,4)
    # Is this the end node
    if currentNode == endNode:
        AppendConsoleLog("Found End with A*","red")
        timeEnded = time.time()
        # Get the time it took to find the end node
        timeTaken = timeEnded - timeStarted
        AppendConsoleLog("Time taken: "+str(round(timeTaken,1))+"s","red")
        AppendConsoleLog("Nodes searched: "+str(len(visited)),"red")
        RetracePath(currentNode)
        global foundEnd
        foundEnd = True
        UpdateLiveConsole(currentNode,5)
        UpdateFrame()
        UpdateLiveConsole(currentNode,6)
        return False
    
    # Get neighbors and update them
    UpdateLiveConsole(currentNode,8)
    neighbors = GetNodeNeighbors(currentNode)
    AppendConsoleLog("This node has "+str(len(neighbors))+" neighbors!")
    AppendConsoleLog("Calculating the f-cost of each neighbor...")
    UpdateLiveConsole(currentNode,9)
    # Iterate through each neighbor
    for neighbor in neighbors:
        neighborNode = neighbor[0]
        edgeLength = neighbor[1]
        
        # Calculate gScore (distance from start to neighbor through currentNode)
        UpdateLiveConsole(currentNode,10)
        tentativeGScore = float(distances[currentNode]) + float(edgeLength)
        
        # If this g score is lower than the neighbors existing g score, update it
        UpdateLiveConsole(currentNode,11)
        if tentativeGScore < distances[neighborNode]:
            UpdateLiveConsole(currentNode,12)
            distances[neighborNode] = tentativeGScore
            parent[neighborNode] = currentNode
            
            # Calculate fScore (gScore + heuristic)
            UpdateLiveConsole(currentNode,13)
            UpdateLiveConsole(currentNode,14)
            fScore = tentativeGScore + Heuristic(neighborNode, endNode)
            AppendConsoleLog("Estimated a nodes distance to the end node")
            AppendConsoleLog("using pythagorean theorem")
            UpdateLiveConsole(currentNode,15)
            UpdateLiveConsole(currentNode,16)
            # Enqueue this node to the priority queue with the new update FScore
            priorityQueue.Enqueue((neighborNode, fScore))
    
    UpdateLiveConsole(currentNode,18)
    return True

dfsStack = utils.Stack()
dfsNextNode = None
def DepthFirst():
    dfsStack.Push(startNode)

distances = {}
# Priority queue (min-heap) to select the node with the smallest known distance
priorityQueue = utils.PriorityQueue()
parent = {}
def Dijkstras():
    for node in nodes:
        distances[node["node_id"]] = float('inf')

    distances[startNode] = 0
    priorityQueue.Enqueue((startNode, 0)) # Start with start node
    
def AStar():
    for node in nodes:
        distances[node["node_id"]] = float('inf')

    distances[startNode] = 0
    fScore = Heuristic(startNode, endNode)  # Initial heuristic estimate
    priorityQueue.Enqueue((startNode, fScore))  # Start with the start node

def RetracePath(endNode):
    currentNode = endNode

    while currentNode != startNode:
        path.append(currentNode)
        currentNode = parent[currentNode]  # Move to the parent node
    
    path.append(startNode)  # Add the start node at the end
    path.reverse()  # Reverse the list to get the path from start to end

def UpdateFrame(currentNode = None, line = 0):
    screen.fill(DARK)
    DrawUI(line)
    DrawGraph(currentNode)
    pygame.display.flip()

# RUN ON PROGRAM START
G, nodes, scaledNodes, edges = LoadGraph()
UpdateFrame()

while running:
    # Get user input
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Check if a node was clicked
            pos = pygame.mouse.get_pos()
            if pos[0] < pathfindingRegion.GetPosition()[0]+pathfindingRegion.GetSize()[0] and pos[0] > pathfindingRegion.GetPosition()[0]:
                if pos[1] < pathfindingRegion.GetPosition()[1]+pathfindingRegion.GetSize()[1] and pos[1] > pathfindingRegion.GetPosition()[1]:
                    # If got to this point click is in pathfinding area
                    selectedNode = None
                    padding = 5
                    for node in scaledNodes:
                        if pos[0] < node["data"]["x"]+padding and pos[0] > node["data"]["x"]-padding:
                            if pos[1] < node["data"]["y"]+padding and pos[1] > node["data"]["y"]-padding:
                                selectedNode = node
                            
                                activelyPathfinding = False
                                pathfinding = False
                                visited = []
                                path = []
                                distances = {}
                                priorityQueue = utils.PriorityQueue()
                                parent = {}
                                foundEnd = False
                                timeTaken = 0
                                timeStarted = 0
                                timeEnded = 0
                    if selectedNode == None:
                        break
                    else:
                        if currentNodeChanging == 0:
                            startNode = selectedNode["node_id"]
                            AppendConsoleLog("Start node selected")
                            currentNodeChanging=1
                        else:
                            endNode = selectedNode["node_id"]
                            AppendConsoleLog("End node selected")
                            currentNodeChanging=0
                        UpdateFrame()
            # Check if a button was clicked
            for button in buttons:
                if button.GetActive() == True:
                    if button.GetClicked(pygame.mouse.get_pos()):
                        if button.GetName() == "Start" and startNode != "" and endNode != "" and foundEnd == False and pathfinding == False:
                            if pathfindingType == 0:
                                DepthFirst()
                            elif pathfindingType == 1:
                                Dijkstras()
                            else:
                                AStar()
                            pathfinding = True
                            activelyPathfinding = True
                            timeStarted = time.time()
                            AppendConsoleLog(" --- PATHFINDING STARTED BY USER --- ")
                            
                        elif button.GetName() == "Next Map":
                            G, nodes, scaledNodes, edges = LoadGraph()
                            
                            startNode = ""
                            endNode = ""
                            activelyPathfinding = False
                            pathfinding = False
                            foundEnd = False
                            visited = []
                            path = []
                            currentNodeChanging = 0
                            distances = {}
                            priorityQueue = utils.PriorityQueue()
                            parent = {}
                            foundEnd = False
                            timeTaken = 0
                            timeStarted = 0
                            timeEnded = 0
                            
                            UpdateFrame()
                        elif button.GetName() == "Pause" and foundEnd == False and activelyPathfinding == True and pathfinding == True:
                            activelyPathfinding = False
                            AppendConsoleLog(" --- PATHFINDING PAUSED BY USER ---")
                        elif button.GetName() == "Resume" and foundEnd == False and pathfinding == True:
                            activelyPathfinding = True
                            AppendConsoleLog(" --- PATHFINDING RESUMED BY USER ---")
                        elif button.GetName() == "Next Step" and startNode != "" and endNode != "" and pathfinding == True and activelyPathfinding == False:
                            if activelyPathfinding == False and foundEnd == False:
                                if pathfindingType == 0:
                                    DepthFirstStep()
                                elif pathfindingType == 1:
                                    DijkstraStep()
                                else:
                                    AStarStep()
                        elif button.GetName() == "Reset":
                            startNode = ""
                            endNode = ""
                            activelyPathfinding = False
                            pathfinding = False
                            foundEnd = False
                            visited = []
                            path = []
                            currentNodeChanging = 0
                            distances = {}
                            priorityQueue = utils.PriorityQueue()
                            parent = {}
                            foundEnd = False
                            timeTaken = 0
                            timeStarted = 0
                            timeEnded = 0
                            
                            AppendConsoleLog(" --- PATHFINDING RESET BY USER ---")
                            
                            UpdateFrame()
                        elif button.GetName() == "Search Type" and pathfinding == False:
                            if pathfindingType == 0:
                                pathfindingType = 1
                                currentPathfindingText = "Dijkstras"
                                AppendConsoleLog("Search type: Dijkstras")
                            elif pathfindingType == 1:
                                pathfindingType = 2
                                currentPathfindingText = "A Star"
                                AppendConsoleLog("Search type: A Star")
                            elif pathfindingType == 2:
                                pathfindingType = 0
                                currentPathfindingText = "Depth-First"
                                AppendConsoleLog("Search type: Depth First")
                
                        elif button.GetName() == "Change Console":
                            if consoleMode == 1:
                                consoleMode = 0
                            else:
                                consoleMode = 1
                            UpdateFrame()
                            

    if activelyPathfinding == True:
        if pathfindingType == 0:
            activelyPathfinding = DepthFirstStep()
        elif pathfindingType == 1:
            activelyPathfinding = DijkstraStep()
        else:
            activelyPathfinding = AStarStep()

AppendConsoleLog(" --- QUITTING APPLICATION ---")
try:
    # Get the number of existing files in the logs folder
    # This is to give the correct name to the log file being created
    number = len(os.listdir("logs"))
except:
    # If there is no folder called "logs" create one
    os.makedirs("logs")
    number = 0
    
# Create the log file and write all the log to it
file = open("logs/log"+str(number)+".txt","w")
for line in consoleFileLog:
    file.write(line+"\n")
file.close()
pygame.quit()
