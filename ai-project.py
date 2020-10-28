#import msvcrt
import sys
import time
import random
from random import shuffle, randrange

width = 16 # width of maze
height = 8 # height of maze
widthLength = ((width*3)+2) # length of the string width including \n and wall (50)
#(*3 because "|  " and "+--"; +2 because \n and wall) use less space("+-") to make it *2
gameComplete = 0 # used to loop the program until the game is complete
stepsTaken = 0 # count how many steps taken until the seeker finds the hider
slowDown = 0 # used to slow down the simulation

# Agent class that contains all the information needed for our agents
class Agent:
    # constructor
    def __init__(self,name,top,bottom,left,right,currentLocation,opposingAgentLastLocation,spotsVisited,spotsSeen,spotsSeeing,path,maze):
        self.name = name
        self.top = top
        self.bottom = bottom
        self.right = right
        self.left = left
        self.currentLocation = currentLocation
        self.opposingAgentLastLocation = opposingAgentLastLocation
        self.spotsSeeing = spotsSeeing
        self.spotsVisited = spotsVisited
        self.spotsSeen = spotsSeen
        self.path = path
        maze = self.fillInBlankMaze(maze)
        self.maze = maze

    # add visited spot to spotsVisited list (uncomment line below to add only if non in list)
    def addSpotVisited(self,spot):
        self.spotsVisited.append(spot) #if spot not in self.spotsVisited else self.spotsVisited

    # add visited spot to spotsSeeing list
    def addSpotSeeing(self,mazeList,spot):
        self.spotsSeeing.append(spot) #if spot not in self.spotsSeeing else self.spotsSeeing
        self.spotsSeen.append(spot) #if spot not in self.spotsSeen else self.spotsSeen
        maze = self.maze
        ourMazeList = list(maze)
        ourMazeList[spot] = mazeList[spot]
        self.maze = "".join(ourMazeList)
        
    # filling in a maze string with "-" instead of spaces (and walls)
    def fillInBlankMaze(self,maze):
        global widthLength
        i=0
        mazeList = list(maze)
        while i < len(mazeList):
            # Use this one to destroy walls and "-"
            if widthLength<i and i < len(mazeList)-widthLength and i % widthLength != 0  and (i+2) % widthLength != 0 and (mazeList[i] == " " or mazeList[i] == "|" or mazeList[i] == "-" or mazeList[i] == "1" or mazeList[i] == "0"):
                mazeList[i] = "~" #or use "-"
            # Use this one to destroy walls 
            #if i % widthLength != 0  and (i+2) % widthLength != 0 and (mazeList[i] == " " or mazeList[i] == "|" or mazeList[i] == "1" or mazeList[i] == "0"):
            #    mazeList[i] = "~"
            # Use this one to keep the walls
            #if mazeList[i] == " " or mazeList[i] == "1" or mazeList[i] == "0":
             #   mazeList[i] = "-"
            i = i + 1
        maze = "".join(mazeList)
        return maze

# Node class that contains information for search algorithms
class Node:
    # constructor
    def __init__(self, location, cost, edges, mazeList):
        self.location = location
        self.cost = cost
        if edges == []:
            self.edges = self.generateEdges(location,edges,mazeList)
        else:
            self.edges = edges
            
    def generateEdges(self,location,edges,mazeList):
        global widthLength
        if mazeList[location+widthLength] == " " or mazeList[location+widthLength] == "1" or mazeList[location+widthLength] == "0":
            edges.append(location+widthLength)
        if mazeList[location-widthLength] == " " or mazeList[location-widthLength] == "1" or mazeList[location-widthLength] == "0":
            edges.append(location-widthLength)
        if mazeList[location-1] == " " or mazeList[location-1] == "1" or mazeList[location-1] == "0":
            edges.append(location-1)
        if mazeList[location+1] == " " or mazeList[location+1] == "1" or mazeList[location+1] == "0":
            edges.append(location+1)
        return edges
            
        

# generates a maze
def make_maze(w = width, h = height):
    vis = [[0] * w + [1] for _ in range(h)] + [[1] * (w + 1)]
    ver = [["|  "] * w + ['|'] for _ in range(h)] + [[]]
    hor = [["+--"] * w + ['+'] for _ in range(h + 1)]
 
    def walk(x, y):
        vis[y][x] = 1
 
        d = [(x - 1, y), (x, y + 1), (x + 1, y), (x, y - 1)]
        shuffle(d)
        for (xx, yy) in d:
            if vis[yy][xx]: continue
            if xx == x: hor[max(y, yy)][x] = "+  "
            if yy == y: ver[y][max(x, xx)] = "   "
            walk(xx, yy)
 
    walk(randrange(w), randrange(h))
 
    s = ""
    for (a, b) in zip(hor, ver):
        s += ''.join(a + ['\n'] + b + ['\n'])
    return s

# replaces the first wall "|" in the maze allowing for an entrance
def make_entrance(maze):
    #print(maze[49:])
    global widthLength
    maze = list(maze)
    maze[widthLength] = " "# widthLength = 50
    maze = "".join(maze)
    return maze

# adds agent to the first available space " " scanning from top to bottom, left to right
def add_agent(maze,agent):
    mazeList = list(maze)
    i = 0
    while i < len(mazeList) and mazeList[i] != " ":
        i = i + 1
    if i != len(mazeList):
        mazeList[i] = agent.name
    maze = "".join(mazeList)
    agent = whatIsAvailable(maze,agent)
    agent.currentLocation = i
    agent.addSpotVisited(i)
    return maze

# adds agent to a spot with a given location (be careful)
def add_agent_spot(maze,agent,spot):
    mazeList = list(maze)
    mazeList[spot] = agent.name
    maze = "".join(mazeList)
    agent = whatIsAvailable(maze,agent)
    agent.currentLocation = spot
    agent.addSpotVisited(i)
    return maze

# just finds a random spot scanning from right to left, bottom to top
def add_agent_random_spot(maze,agent):
    global widthLength
    mazeList = list(maze)
    i = len(mazeList)-1
    gettingSpot=0
    while gettingSpot == 0:
        if i <= 0:
            i = len(mazeList)-1
        i = i - 1
        if mazeList[i] == " " and 30 < randrange(32): #and mazeList[i-widthLength] == "+":
            gettingSpot=1
    mazeList[i] = agent.name
    maze = "".join(mazeList)
    agent = whatIsAvailable(maze,agent)
    agent.currentLocation = i
    agent.addSpotVisited(i)
    return maze

# resets agents data
def agent_reset(agent):
    agent.top = -1
    agent.bottom = -1
    agent.left = -1
    agent.right = -1
    return agent

# checks around the seeker for the hider, if found gameComplete = 1 and the game is over
def checkForHider(mazeList, agent,i):
    global gameComplete
    global widthLength
    if i-widthLength < len(mazeList)-1 and 0 <= i -widthLength and mazeList[i-widthLength] == "1":# widthLength = 50
        gameComplete = 1
    if i-1 < len(mazeList)-1 and 0 <= i-1 and mazeList[i-1] == "1":
        gameComplete = 1
    if i+1 < len(mazeList)-1 and 0 <= i+1 and mazeList[i+1] == "1":
        gameComplete = 1
    if i+widthLength < len(mazeList)-1 and 0 <= i+widthLength and mazeList[i+widthLength] == "1":
        gameComplete = 1

# looks around the agent for " " and updates its data accordingly
def whatIsAvailable(maze, agent):
    global width
    global widthLength
    mazeList = list(maze)
    i = 0
    while i < len(mazeList) and mazeList[i] != agent.name:
        i = i + 1
    if widthLength <= i and mazeList[i-widthLength] == " ":# widthLength = 50
        agent.top = i-widthLength
    if mazeList[i-1] == " ":#i % width != 0 and
        agent.left = i-1
    if mazeList[i+1] == " ":#i+1 % width != 0 and
        agent.right = i+1
    if i < len(mazeList) - widthLength and mazeList[i+widthLength] == " ":
        agent.bottom = i+((width*3)+2)
    checkForHider(mazeList, agent,i)
    return agent

# checks for a new unvisited spot for an agent to move to
def checkForNewSpot(maze, agent):
    global widthLength
    mazeList = list(maze)
    i = 0
    check = 0
    while i < len(mazeList) and mazeList[i] != agent.name:
        i = i + 1
    if agent.top != -1 and agent.top not in agent.spotsVisited:
        check = 1
    if agent.left != -1 and agent.left not in agent.spotsVisited:
        check = 1
    if agent.right != -1 and agent.right not in agent.spotsVisited:
        check = 1
    if agent.bottom != -1 and agent.bottom not in agent.spotsVisited:
        check = 1
    return check

# randomly traverses through the maze
def randomTraverse(maze, agent):
    global stepsTaken
    mazeList = list(maze)
    i = 0
    choices = 0
    choicesList = [-1,-1,-1,-1]
    while i < len(mazeList) and mazeList[i] != agent.name:
        i = i + 1
    mazeList[i] = " "
    if agent.top != -1:
        choicesList[choices] = agent.top # if spot available add this to our list
        choices = choices + 1
    if agent.bottom != -1:
        choicesList[choices] = agent.bottom # so we can choose between what's available
        choices = choices + 1
    if agent.left != -1:
        choicesList[choices] = agent.left # [old code below v]
        choices = choices + 1
    if agent.right != -1:
        choicesList[choices] = agent.right #mazeList[agent.right] = agent.name
        choices = choices + 1

    choicesList = choicesList[:choices]
    choice = random.sample(choicesList,1)
    choice = choice[0]
    mazeList[choice] = agent.name
    agent.addSpotVisited(choice)
    agent.currentLocation = choice
    agent = agent_reset(agent)
    maze = "".join(mazeList)
    agent = whatIsAvailable(maze,agent)
    stepsTaken = stepsTaken + 1
    return maze

# returns the element right before the currentLocation in the spotsVisited array
def randomTraverseBackwards(agent, currentLocation):
    index = agent.spotsVisited.index(currentLocation)
    return agent.spotsVisited[index-1]

# looks for a random new spot to go to, traverses backwards if not found
def randomTraverseNewSpots(maze, agent):
    global stepsTaken
    mazeList = list(maze)
    i = 0
    choices = 0
    choicesList = [-1,-1,-1,-1]
    while i < len(mazeList) and mazeList[i] != agent.name:
        i = i + 1
    agent = whatIsAvailable(maze,agent)

    # traverses backwards if no new random spots available until one is found
    if checkForNewSpot(maze,agent) == 0:
        choice = randomTraverseBackwards(agent,i)
    else:
        if agent.top != -1 and agent.top not in agent.spotsVisited:
            choicesList[choices] = agent.top # if spot available add this to our list
            choices = choices + 1
        if agent.bottom != -1 and agent.bottom not in agent.spotsVisited:
            choicesList[choices] = agent.bottom # so we can choose between what's available
            choices = choices + 1
        if agent.left != -1 and agent.left not in agent.spotsVisited:
            choicesList[choices] = agent.left # [old code below v]
            choices = choices + 1
        if agent.right != -1 and agent.right not in agent.spotsVisited:
            choicesList[choices] = agent.right #mazeList[agent.right] = agent.name
            choices = choices + 1
        choicesList = choicesList[:choices]
        choice = random.sample(choicesList,1)
        choice = choice[0]
    agent.addSpotVisited(choice)
    mazeList[i] = " "
    mazeList[choice] = agent.name
    agent.currentLocation = choice
    agent = agent_reset(agent)
    maze = "".join(mazeList)
    agent = whatIsAvailable(maze,agent)
    stepsTaken = stepsTaken + 1
    return maze

# updates the vertical sight(all " ") above the agent
def updateTop(mazeList,agent,currentLocation):
    global widthLength
    if (currentLocation - (widthLength*2)-1) <= 0:
        return
    i = currentLocation - widthLength
    # checking to see if the space to the left of you is a space and the space right above it (past the line of walls) so we can
    # expand the view of the agent to the proper length of the maze halls
    left = True
    right = True
    # here we make sure the spaces to the left or right are empty along with the ones right above so we can
    # use this line of sight. If there is something obstructing right here then we don't even expand this way
    if (mazeList[currentLocation-1] != " " and mazeList[currentLocation-1] != "1" and mazeList[currentLocation-1] != "0") and (mazeList[(currentLocation-(widthLength))-1] != " " and mazeList[(currentLocation-(widthLength))-1] != "1" and mazeList[(currentLocation-(widthLength))-1] != "0"):
        left = False
    if (mazeList[currentLocation+1] != " " and mazeList[currentLocation+1] != "1" and mazeList[currentLocation+1] != "0") and (mazeList[(currentLocation-(widthLength))+1] != " " and mazeList[(currentLocation-(widthLength))+1] != "1" and mazeList[(currentLocation-(widthLength))+1] != "0"):
        right = False
    # we add all the spots directly above the agent
    while 0 < i:
        if mazeList[i] != " " and mazeList[i] != "1" and mazeList[i] != "0":
            break
        agent.addSpotSeeing(mazeList,i)
        i = i - widthLength
    agent.addSpotSeeing(mazeList,i) # uncomment these when we add array to agent that includes what's actually seen
    #agent.addSpotSeen(i) # so further path decision making can be made
        
    # then we add the spaces to the left and above the agent (there's two spaces in vertical hallways) this also
    # makes it to where the agent can see more if given the leverage. Example, if the agent is up against the left
    # part of a wall, then we don't even go in this loop, but if he's on the right part of the wall then he can see
    # all the left of the vertical hallway along with parts of the corridor that can extend to new hallways. This can
    # allow for advance decision making as the agent can see down a hallway to decipher if there's more paths
    # in the hallway. Not only that but this also allows and agent to see around a corner, but isn't actually able to
    # see further paths from this angle because this loop only adds up to two spots to the left of the agent going
    # upward. (eventually will change the agent to have an array with what's actually seen so path decision making
    # can be used)
    if left == True:
        i = currentLocation - widthLength -1
        while 0 < i:
            if mazeList[i] != " " and mazeList[i] != "1" and mazeList[i] != "0":
                break
            agent.addSpotSeeing(mazeList,i)
            agent.addSpotSeeing(mazeList,i-1)
            # if mazeList[i-1] == " " or mazeList[i-1] == "1"  or mazeList[i-1] == "0":
                # agent.addSpotSeeing(mazeList,i-1)
            i = i - widthLength
        agent.addSpotSeeing(mazeList,i) # uncomment these when we add array to agent that includes what's actually seen
        agent.addSpotSeeing(mazeList,i-1) # uncomment these when we add array to agent that includes what's actually seen
    # we do the same with the right side
    if right == True:
        i = currentLocation - widthLength +1
        while 0 < i:
            if mazeList[i] != " " and mazeList[i] != "1" and mazeList[i] != "0":
                break
            agent.addSpotSeeing(mazeList,i)
            agent.addSpotSeeing(mazeList,i+1)
            #if mazeList[i+1] == " " or mazeList[i+1] == "1" or mazeList[i+1] == "0":
            #    agent.addSpotSeeing(mazeList,i+1)
            i = i - widthLength
        agent.addSpotSeeing(mazeList,i) # uncomment these when we add array to agent that includes what's actually seen
        agent.addSpotSeeing(mazeList,i+1) # uncomment these when we add array to agent that includes what's actually seen

# updates the vertical sight(all " ") below the agent
def updateBottom(mazeList,agent,currentLocation):
    global widthLength
    if len(mazeList) < (currentLocation + (widthLength*2)+1):
        return
    i = currentLocation + widthLength
    # checking to see if the space to the left of you is a space and the space right above it (past the line of walls) so we can
    # expand the view of the agent to the proper length of the maze halls
    left = True
    right = True
    if (mazeList[currentLocation-1] != " " and mazeList[currentLocation-1] != "1" and mazeList[currentLocation-1] != "0") and (mazeList[(currentLocation+(widthLength))-1] != " " and mazeList[(currentLocation+(widthLength))-1] != "1"and mazeList[(currentLocation+(widthLength))-1] != "0"):
        left = False
    if (mazeList[currentLocation+1] != " " and mazeList[currentLocation+1] != "1" and mazeList[currentLocation+1] != "0") and (mazeList[(currentLocation+(widthLength))+1] != " " and mazeList[(currentLocation+(widthLength))+1] != "1" and mazeList[(currentLocation+(widthLength))+1] != "0"):
        right = False
    while i < len(mazeList)-1:
        if mazeList[i] != " " and mazeList[i] != "1" and mazeList[i] != "0":
            break
        agent.addSpotSeeing(mazeList,i)
        i = i + widthLength
    agent.addSpotSeeing(mazeList,i) # uncomment these when we add array to agent that includes what's actually seen
    #agent.addSpotSeen(i) # so further path decision making can be made
    if left == True:
        i = currentLocation + widthLength - 1
        while i < len(mazeList)-1:
            if mazeList[i] != " " and mazeList[i] != "1" and mazeList[i] != "0":
                break
            agent.addSpotSeeing(mazeList,i)
            agent.addSpotSeeing(mazeList,i-1)
            #if mazeList[i-1] == " " or mazeList[i-1] == "1" or mazeList[i-1] == "0":
            #    agent.addSpotSeeing(mazeList,i-1)
            i = i + widthLength
        agent.addSpotSeeing(mazeList,i) # uncomment these when we add array to agent that includes what's actually seen
        agent.addSpotSeeing(mazeList,i-1) # uncomment these when we add array to agent that includes what's actually seen
    if right == True:
        i = currentLocation + widthLength + 1
        while i < len(mazeList)-1:
            if mazeList[i] != " " and mazeList[i] != "1" and mazeList[i] != "0":
                break
            agent.addSpotSeeing(mazeList,i)
            agent.addSpotSeeing(mazeList,i+1)
            #if mazeList[i+1] == " " or mazeList[i+1] == "1" or mazeList[i+1] == "0":
            #    agent.addSpotSeeing(mazeList,i+1)
            i = i + widthLength
        agent.addSpotSeeing(mazeList,i) # uncomment these when we add array to agent that includes what's actually seen
        agent.addSpotSeeing(mazeList,i+1) # uncomment these when we add array to agent that includes what's actually seen

# updates the horizontal sight(all " ") to the left of the agent
def updateLeft(mazeList,agent,currentLocation):
    global widthLength
    i = currentLocation - 1
    top = True
    bottom = True
    if (mazeList[currentLocation-widthLength] != " " and mazeList[currentLocation-widthLength] != "1" and mazeList[currentLocation-widthLength] != "0") and (mazeList[(currentLocation-(widthLength))-1] != " " and mazeList[(currentLocation-(widthLength))-1] != "1"and mazeList[(currentLocation-(widthLength))-1] != "0"):
        top = False
    if (mazeList[currentLocation+widthLength] != " " and mazeList[currentLocation+widthLength] != "1" and mazeList[currentLocation+widthLength] != "0") and (mazeList[(currentLocation+(widthLength))-1] != " " and mazeList[(currentLocation+(widthLength))-1] != "1" and mazeList[(currentLocation+(widthLength))-1] != "0"):
        bottom = False
    while mazeList[i] != "|" and mazeList[i] != "+" and mazeList[i] != "-":
        if mazeList[i] != " " and mazeList[i] != "1" and mazeList[i] != "0":
            break
        agent.addSpotSeeing(mazeList,i)
        agent.addSpotSeeing(mazeList,i-widthLength)
        agent.addSpotSeeing(mazeList,i+widthLength)
        i = i - 1
    agent.addSpotSeeing(mazeList,i) # uncomment these when we add array to agent that includes what's actually seen
    agent.addSpotSeeing(mazeList,i-widthLength) # uncomment these when we add array to agent that includes what's actually seen
    agent.addSpotSeeing(mazeList,i+widthLength) # uncomment these when we add array to agent that includes what's actually seen
    #agent.addSpotSeen(i) # so further path decision making can be made
    if top == True:
        i = currentLocation - widthLength - 1
        while mazeList[i] != "|" and mazeList[i] != "+" and mazeList[i] != "-":
            if mazeList[i] != " " and mazeList[i] != "1" and mazeList[i] != "0":
                break
            agent.addSpotSeeing(mazeList,i)
            # possibly delete
            #if mazeList[i-widthLength] == " " or mazeList[i-widthLength] == "1" or mazeList[i-widthLength] == "0":
             #   agent.addSpotSeeing(i-widthLength)
            #    agent.addSpotSeen(i-widthLength)
            i = i - 1
        agent.addSpotSeeing(mazeList,i) # uncomment these when we add array to agent that includes what's actually seen
    if bottom == True:
        i = currentLocation + widthLength - 1
        while mazeList[i] != "|" and mazeList[i] != "+" and mazeList[i] != "-":
            if mazeList[i] != " " and mazeList[i] != "1" and mazeList[i] != "0":
                break
            agent.addSpotSeeing(mazeList,i)
            #if mazeList[i+widthLength] == " " or mazeList[i+widthLength] == "1" or mazeList[i+widthLength] == "0":
            #    agent.addSpotSeeing(i+widthLength)
            #    agent.addSpotSeen(i+widthLength)
            i = i - 1
        agent.addSpotSeeing(mazeList,i) # uncomment these when we add array to agent that includes what's actually seen

# updates the horizontal sight(all " ") to the right of the agent
def updateRight(mazeList,agent,currentLocation):
    global widthLength
    i = currentLocation + 1
    top = True
    bottom = True
    if (mazeList[currentLocation-widthLength] != " " and mazeList[currentLocation-widthLength] != "1" and mazeList[currentLocation-widthLength] != "0") and (mazeList[(currentLocation-(widthLength))+1] != " " and mazeList[(currentLocation-(widthLength))+1] != "1"and mazeList[(currentLocation-(widthLength))+1] != "0"):
        top = False
    if (mazeList[currentLocation+widthLength] != " " and mazeList[currentLocation+widthLength] != "1" and mazeList[currentLocation+widthLength] != "0") and (mazeList[(currentLocation+(widthLength))+1] != " " and mazeList[(currentLocation+(widthLength))+1] != "1" and mazeList[(currentLocation+(widthLength))+1] != "0"):
        bottom = False
    while mazeList[i] != "|" and mazeList[i] != "+" and mazeList[i] != "-":
        if mazeList[i] != " " and mazeList[i] != "1" and mazeList[i] != "0":
            break
        agent.addSpotSeeing(mazeList,i)
        agent.addSpotSeeing(mazeList,i-widthLength)
        agent.addSpotSeeing(mazeList,i+widthLength)
        i = i + 1
    agent.addSpotSeeing(mazeList,i) # uncomment these when we add array to agent that includes what's actually seen
    agent.addSpotSeeing(mazeList,i-widthLength) # uncomment these when we add array to agent that includes what's actually seen
    agent.addSpotSeeing(mazeList,i+widthLength) # uncomment these when we add array to agent that includes what's actually seen
    #agent.addSpotSeen(i) # so further path decision making can be made
    if top == True:
        i = currentLocation - widthLength + 1
        while mazeList[i] != "|"and mazeList[i] != "+" and mazeList[i] != "-":
            if mazeList[i] != " " and mazeList[i] != "1" and mazeList[i] != "0":
                break
            agent.addSpotSeeing(mazeList,i)
            # possibly delete
            #if mazeList[i-widthLength] == " " or mazeList[i-widthLength] == "1" or mazeList[i-widthLength] == "0":
            #    agent.addSpotSeeing(i-widthLength)
             #   agent.addSpotSeen(i-widthLength)
            i = i + 1
        agent.addSpotSeeing(mazeList,i) # uncomment these when we add array to agent that includes what's actually seen
    if bottom == True:
        i = currentLocation + widthLength + 1
        while mazeList[i] != "|" and mazeList[i] != "+" and mazeList[i] != "-":
            if mazeList[i] != " " and mazeList[i] != "1" and mazeList[i] != "0":
                break
            agent.addSpotSeeing(mazeList,i)
            #if mazeList[i+widthLength] == " " or mazeList[i+widthLength] == "1" or mazeList[i+widthLength] == "0":
             #   agent.addSpotSeeing(i+widthLength)
             #   agent.addSpotSeen(i+widthLength)
            i = i + 1
        agent.addSpotSeeing(mazeList,i) # uncomment these when we add array to agent that includes what's actually seen

# updates the sight of the agent (updates agent.spotsSeen/spotsSeeing)
def updateSight(mazeList,agent,currentLocation):
    updateTop(mazeList,agent,currentLocation)
    updateBottom(mazeList,agent,currentLocation)
    updateLeft(mazeList,agent,currentLocation)
    updateRight(mazeList,agent,currentLocation)

# looks through 2 arrays for a certain node and returns true if it's found and replaces it in the array if the cost is less
def nodeCostCheck(nodesAvailable,nodesVisited,node):
    for nodeTemp in nodesVisited:
        if nodeTemp.location == node.location:
            return nodesAvailable
    for nodeTemp in nodesAvailable:
        if nodeTemp.location == node.location:
            if node.cost < nodeTemp.cost:
                nodesAvailable.remove(nodeTemp)
                nodesAvailable.append(node)
            return nodesAvailable
    nodesAvailable.append(node)
    return nodesAvailable

# returns a list of indices in the maze string for a proper path using uniform cost searching algorithms
def uniformCostPath(mazeList, currentLocation, destination):
    global widthLength
    node = Node(currentLocation,0, [], mazeList)
    nodesVisited = [node]
    nodesAvailable = []
    i = currentLocation
    cost = 0
    minCost = sys.maxsize
    pathComplete = 0
    result = []
    while pathComplete == 0:
        cost = cost + 1
        if widthLength <= i and (mazeList[i-widthLength] == " " or mazeList[i-widthLength] == "1" or mazeList[i-widthLength] == "0"):# widthLength = 50
            node = Node(i-widthLength, cost, [], mazeList)
            nodesAvailable = nodeCostCheck(nodesAvailable,nodesVisited,node)
        if mazeList[i-1] == " " or mazeList[i-1] == "1" or mazeList[i-1] == "0":#i % width != 0 and
            node = Node(i-1, cost, [], mazeList)
            nodesAvailable = nodeCostCheck(nodesAvailable,nodesVisited,node)
        if mazeList[i+1] == " " or mazeList[i+1] == "1" or mazeList[i+1] == "0":#i+1 % width != 0 and
            node = Node(i+1, cost, [], mazeList)
            nodesAvailable = nodeCostCheck(nodesAvailable,nodesVisited,node)
        if i < len(mazeList) - widthLength and (mazeList[i+widthLength] == " " or mazeList[i+widthLength] == "1" or mazeList[i+widthLength] == "0"):
            node = Node(i+widthLength, cost, [], mazeList)
            nodesAvailable = nodeCostCheck(nodesAvailable,nodesVisited,node) #if node not in nodesAvailable and nodesVisited else nodesAvailable
            
        # Checking if available nodes list is empty
        if nodesAvailable == []:
            #print("HERE")
            pathComplete = -1
            
        for node in nodesAvailable:
            #print("nodes available = "+str(node.location) +" "+str(node.cost))
            if node.cost < minCost or (node.cost == minCost and node.location == destination):
                currentNode = node
                minCost = node.cost
        # Reach destination
        if currentNode is not None:
            #print("yo"+str(currentNode.location))
            nodesAvailable.remove(currentNode)
            nodesVisited.append(currentNode)
            cost = currentNode.cost
            i = currentNode.location
            if currentNode.location == destination:
                pathComplete = 1
        else:
            pathComplete = -1
        minCost = sys.maxsize
        currentNode = None
    if pathComplete == 1:
        result.append(nodesVisited[len(nodesVisited)-1])
        for node in nodesVisited[::-1]:
            for edges in result[len(result)-1].edges:
                if edges == node.location and node.cost < result[len(result)-1].cost:
                    result.append(node)
        result = result[::-1]
        #result = result[1:]
    return result

# looks for the hider based on what the seeking agent sees (agent.spotsSeeing)
def checkForHiderSight(mazeList,agent):
    result = 0
    for i in agent.spotsSeeing:
        if mazeList[i] == "1":
            result = i
            agent.opposingAgentLastLocation = i
            agent.path = uniformCostPath(list(agent.maze), agent.currentLocation, i)
    return result

# finds the shortest path between the seeker and hider(or last seen) and returns the node that goes towards that path
def seekerToHider(mazeList,agent,currentLocation,hiderLocation):
    if(currentLocation == hiderLocation):
        agent.opposingAgentLastLocation = -1
        return currentLocation
    global widthLength
    result = currentLocation
    seekerLengthToSlashN = 0
    hiderLengthToSlashN = 0
    i = hiderLocation
    while mazeList[i] != "\n":
        i = i + 1
        hiderLengthToSlashN = hiderLengthToSlashN + 1
    i = currentLocation
    while mazeList[i] != "\n":
        i = i + 1
        seekerLengthToSlashN = seekerLengthToSlashN + 1
    
    if result == currentLocation:
        if agent.bottom != -1 and (currentLocation+widthLength <= hiderLocation or (hiderLengthToSlashN == seekerLengthToSlashN and currentLocation < hiderLocation)or (seekerLengthToSlashN < hiderLengthToSlashN and currentLocation < hiderLocation)):# hider below
            result = currentLocation + widthLength
        elif agent.top != -1 and (hiderLocation+widthLength <= currentLocation or (hiderLengthToSlashN == seekerLengthToSlashN and hiderLocation < currentLocation) or (hiderLengthToSlashN < seekerLengthToSlashN and hiderLocation < currentLocation)): # hider above
            result = currentLocation - widthLength
        elif agent.right != -1 and hiderLengthToSlashN < seekerLengthToSlashN: # hider to the right
            result = currentLocation + 1
        elif agent.left != -1 and seekerLengthToSlashN < hiderLengthToSlashN:# hider to the left
            result = currentLocation - 1
    if result == currentLocation:
        if agent.bottom != -1 and currentLocation < hiderLocation:# hider below
            result = currentLocation + widthLength
        elif agent.top != -1 and hiderLocation < currentLocation: # hider above
            result = currentLocation - widthLength
        elif agent.right != -1 and currentLocation < hiderLocation: # hider to the right
            result = currentLocation + 1
        elif agent.left != -1 and hiderLocation < currentLocation:# hider to the left
            result = currentLocation - 1
            
    # if we get to the last known location or there is a problem getting there
    if agent.opposingAgentLastLocation == result:
        agent.opposingAgentLastLocation = -1
        
    return result

# same as randomTraverseNewSpots but also has vision along with continuing in a direction until a wall is hit
def randomTraverseNewSpotsSight(maze, agent):
    global stepsTaken
    mazeList = list(maze)
    i = 0
    choices = 0
    choicesList = [-1,-1,-1,-1]
    while i < len(mazeList) and mazeList[i] != agent.name:
        i = i + 1
    agent = whatIsAvailable(maze,agent)
    agent.spotsSeeing.clear()
    updateSight(mazeList,agent,i)
    hiderLocation = checkForHiderSight(mazeList,agent)
    # check if there's a hider in sight
    if hiderLocation != 0:
        #print("YESS")
        choice = seekerToHider(mazeList,agent,i,hiderLocation)
    # if the agent still has a location for the opposing agent, then pursue that location
    elif agent.opposingAgentLastLocation != -1:
        #print("HERE! " + str(agent.opposingAgentLastLocation))
        choice = seekerToHider(mazeList,agent,i,agent.opposingAgentLastLocation)
        #print("choice= " + str(choice))
    # otherwise, traverse backwards if no new random spots available until one is found
    elif checkForNewSpot(maze,agent) == 0:
        choice = randomTraverseBackwards(agent,i)
    # else we choose a random path by gathering what's available 
    else:
        if agent.top != -1 and agent.top not in agent.spotsVisited:
            choicesList[choices] = agent.top # if spot available add this to our list
            choices = choices + 1
        if agent.bottom != -1 and agent.bottom not in agent.spotsVisited:
            choicesList[choices] = agent.bottom # so we can choose between what's available
            choices = choices + 1
        if agent.left != -1 and agent.left not in agent.spotsVisited:
            choicesList[choices] = agent.left # [old code below v]
            choices = choices + 1
        if agent.right != -1 and agent.right not in agent.spotsVisited:
            choicesList[choices] = agent.right #mazeList[agent.right] = agent.name
            choices = choices + 1
        choicesList = choicesList[:choices]
        choice = random.sample(choicesList,1)
        choice = choice[0]
    agent.addSpotVisited(choice)
    mazeList[i] = " "
    mazeList[choice] = agent.name
    agent.currentLocation = choice
    agent = agent_reset(agent)
    maze = "".join(mazeList)
    agent = whatIsAvailable(maze,agent)
    stepsTaken = stepsTaken + 1
    updateSight(mazeList,agent,choice) #debugging purposes (so we can see what he's seeing with the print)
    return maze

# Performs a random search until it finds the hiding agent, then it will use A* searching algorithm to find the best path to the hiders last known location    
def randomTraverseUniformCostSeek(maze, agent):
    global stepsTaken
    mazeList = list(maze)
    i = 0
    choices = 0
    choicesList = [-1,-1,-1,-1]
    while i < len(mazeList) and mazeList[i] != agent.name:
        i = i + 1
    agent = whatIsAvailable(maze,agent)
    agent.spotsSeeing.clear()
    updateSight(mazeList,agent,i)
    checkForHiderSight(mazeList,agent)
    if agent.path != []:
        if agent.currentLocation != agent.path[len(agent.path)-1].location:
            for spot in agent.path:
                if spot.location == i:
                    index = agent.path.index(spot)
                    choice = agent.path[index+1]
                    break
            choice = choice.location
        else:
            agent.path = []
    # otherwise, traverse backwards if no new random spots available until one is found
    elif checkForNewSpot(maze,agent) == 0:
        choice = randomTraverseBackwards(agent,i)
    # else we choose a random path by gathering what's available 
    else:
        if agent.top != -1 and agent.top not in agent.spotsVisited:
            choicesList[choices] = agent.top # if spot available add this to our list
            choices = choices + 1
        if agent.bottom != -1 and agent.bottom not in agent.spotsVisited:
            choicesList[choices] = agent.bottom # so we can choose between what's available
            choices = choices + 1
        if agent.left != -1 and agent.left not in agent.spotsVisited:
            choicesList[choices] = agent.left # [old code below v]
            choices = choices + 1
        if agent.right != -1 and agent.right not in agent.spotsVisited:
            choicesList[choices] = agent.right #mazeList[agent.right] = agent.name
            choices = choices + 1
        choicesList = choicesList[:choices]
        choice = random.sample(choicesList,1)
        choice = choice[0]
        
    agent.addSpotVisited(choice)
    mazeList[i] = " "
    mazeList[choice] = agent.name
    agent.currentLocation = choice
    agent = agent_reset(agent)
    maze = "".join(mazeList)
    agent = whatIsAvailable(maze,agent)
    stepsTaken = stepsTaken + 1
    updateSight(mazeList,agent,choice) #debugging purposes (so we can see what he's seeing with the print)
    return maze

# main
if __name__ == '__main__':
    maze = make_maze()
    #maze = make_entrance(maze)
    seeker = Agent("0",-1,-1,-1,-1,-1,-1,[],[],[],[],maze) #(name,top,bottom,left,right,currentLocation,opposingAgentLastLocation,spotsVisited,spotsSeen,spotsSeeing,path,mazeList)
    hider = Agent("1",-1,-1,-1,-1,-1,-1,[],[],[],[],maze)
    maze = add_agent(maze, seeker)
    maze = add_agent_random_spot(maze,hider)
    updateSight(list(maze),seeker,seeker.currentLocation)
    #testing = uniformCostPath(list(maze),seeker.currentLocation,hider.currentLocation)
    while gameComplete == 0:
        # Random search
        #maze = randomTraverse(maze,seeker)

        # Random search to new locations
        #maze = randomTraverseNewSpots(maze,seeker)

        # Random search to new locations with visual clues (deprecated, can get caught in a loop with current visual info; creating proper path to the hider with dijkstra/a* algos to fix this)
        #maze = randomTraverseNewSpotsSight(maze,seeker) 

        # Random search with uniform cost path seeking 
        maze = randomTraverseUniformCostSeek(maze,seeker) 

        # if you press a key it slows down the simulation
        # This only works on Windows        
        # if msvcrt.kbhit():
           # key_stroke = msvcrt.getch()
           # print(key_stroke)
           # if slowDown == 0:
               # slowDown = 1
           # else:
               # slowDown = 0
        if slowDown == 0:
            time.sleep(0.06)
        else:
            time.sleep(0.6) # replace with putting this(traverse/keyboardinput)^ in tick from game engine and prints in render(or actual 3d maze)
        
        #print("SEEKER CURRENT LOCATION = "+str(seeker.currentLocation))
        #testing = uniformCostPath(list(seeker.maze),seeker.currentLocation,57)
        #for test in testing:
        #    print("UNIFORM COST PATH = "+str(test.location))
        print("AGENT MAZE = ")
        print(seeker.maze)
        print("top = "+str(seeker.top)+"\nbottom = "+str(seeker.bottom)+"\nleft= "+str(seeker.left)+"\nright = "+str(seeker.right)+"\n")
        print(maze)
    print("Steps Taken = "+str(stepsTaken))
    #print("Spots Visited = "+str(seeker.spotsVisited))
    #print("Current Location = "+str(seeker.currentLocation))
