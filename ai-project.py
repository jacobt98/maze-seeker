#import msvcrt
import sys
import time
import random
from random import shuffle, randrange
import pandas as pd
import numpy as np
from sklearn import preprocessing
from sklearn import linear_model
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import mean_squared_error

width = 16 # width of maze
height = 8 # height of maze
widthLength = ((width*3)+2) # length of the string width including \n and wall (50)
#(*3 because "|  " and "+--"; +2 because \n and wall) use less space("+-") to make it *2
gameComplete = 0 # used to loop the program until the game is complete
rounds = 0 # used to know how many rounds the agents have gone through
stepsTaken = 0 # count how many steps taken until the seeker finds the hider
allAvailableSpaces = 0 # used to find out if the hider should continue discovering
maxHiderSteps = 200 # how many steps the hider can take
hiderSteps = 0 # how many steps the hider has taken before the hunt begins
hiderDiscoveryMode = 0 # used to determine if the hider should continue to look for spots
hiderHiding = 0 # used to place the seeker in once the hider is finished
slowDown = 0 # used to slow down the simulation

# Agent class that contains all the information needed for our agents
class Agent:
    # constructor
    def __init__(self,name,top,bottom,left,right,currentLocation,opposingAgentLastLocation,wallsAroundAgent,stepsFromEntrance,pathDecisionChoicesFromEntrance,spotsVisited,spotsSeen,spotsSeeing,path,maze):
        self.name = name
        self.top = top
        self.bottom = bottom
        self.right = right
        self.left = left
        self.currentLocation = currentLocation
        self.opposingAgentLastLocation = opposingAgentLastLocation
        self.wallsAroundAgent = wallsAroundAgent
        self.stepsFromEntrance = stepsFromEntrance
        self.pathDecisionChoicesFromEntrance = pathDecisionChoicesFromEntrance
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

def remove_seeker(maze):
    i=0
    mazeList = list(maze)
    while i < len(mazeList):
        # Use this one to destroy walls and "-"
        if widthLength<i and i < len(mazeList)-widthLength and i % widthLength != 0  and (i+2) % widthLength != 0 and (mazeList[i] == "0"):
            mazeList[i] = " " #or use "-"
        i = i + 1
    maze = "".join(mazeList)
    return maze
        
# finds out how many spaces there are in the maze given
def spotsKnown(maze):
    global widthLength
    i=0
    spotsKnown = 0
    mazeList = list(maze)
    while i < len(mazeList):
        # Use this one to destroy walls and "-"
        if widthLength<i and i < len(mazeList)-widthLength and i % widthLength != 0  and (i+2) % widthLength != 0 and (mazeList[i] == " "):
            spotsKnown = spotsKnown + 1
        i = i + 1
    return spotsKnown
    
# finds the number of walls around a location
def wallsAround(maze,currentLocation):
    global widthLength
    mazeList = list(maze)
    numberOfWalls = 0
    if widthLength<currentLocation and currentLocation < len(mazeList)-widthLength and currentLocation% widthLength != 0  and (currentLocation+2) % widthLength != 0 and mazeList[currentLocation + 1] != " ":
        numberOfWalls = numberOfWalls + 1
    if widthLength<currentLocation and currentLocation < len(mazeList)-widthLength and currentLocation % widthLength != 0  and (currentLocation+2) % widthLength != 0 and mazeList[currentLocation - 1] != " ":
        numberOfWalls = numberOfWalls + 1
    if widthLength<currentLocation and currentLocation < len(mazeList)-widthLength and currentLocation % widthLength != 0  and (currentLocation+2) % widthLength != 0 and mazeList[currentLocation +widthLength] != " ":
        numberOfWalls = numberOfWalls + 1
    if widthLength<currentLocation and currentLocation < len(mazeList)-widthLength and currentLocation % widthLength != 0  and (currentLocation+2) % widthLength != 0 and mazeList[currentLocation -widthLength] != " ":
        numberOfWalls = numberOfWalls + 1
    return numberOfWalls
    
# finds the number of steps from a location to the entrance of the maze
def stepsFromEntranceFunc(maze,currentLocation):
    path = uniformCostPath(list(maze), currentLocation, 51)
    length = len(path)
    return length

# finds all the path decision choices leading up to a location from the beginning of the maze
def pathDecisionChoicesFromEntranceFun(maze,currentLocation):
    global widthLength
    mazeList = list(maze)
    path = uniformCostPath(mazeList, currentLocation, 51)
    pathDecisions = 0
    spaces = 0
    for spot in path:
        if mazeList[spot.location+1] == " " and widthLength<spot.location and spot.location < len(mazeList)-widthLength and spot.location % widthLength != 0  and (spot.location+2) % widthLength != 0:
            spaces = spaces + 1
        if mazeList[spot.location-1] == " " and widthLength<spot.location and spot.location < len(mazeList)-widthLength and spot.location % widthLength != 0  and (spot.location+2) % widthLength != 0:
            spaces = spaces + 1
        if mazeList[spot.location+widthLength] == " " and widthLength<spot.location and spot.location < len(mazeList)-widthLength and spot.location % widthLength != 0  and (spot.location+2) % widthLength != 0:
            spaces = spaces + 1
        if mazeList[spot.location-widthLength] == " " and widthLength<spot.location and spot.location < len(mazeList)-widthLength and spot.location % widthLength != 0  and (spot.location+2) % widthLength != 0:
            spaces = spaces + 1
        if 2 < spaces:
            pathDecisions = pathDecisions + 1
        if 3 < spaces:
            pathDecisions = pathDecisions + 1
        spaces = 0
    return pathDecisions
    
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

# Performs a random search until it finds the hiding agent, then it will use uniform cost searching algorithm to find the best path to the hiders last known location    
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
    # making sure we haven't reached the end of our path if the agent has one
    if agent.path != [] and agent.currentLocation == agent.path[len(agent.path)-1].location:
            agent.path = []
    # if our agent has a path then that's our first priority for a means of traversing
    if agent.path != []:
        for spot in agent.path:
            if spot.location == i:
                index = agent.path.index(spot)
                choice = agent.path[index+1]
                break
        try:
            choice = choice.location
        except:
            agent.path = []
            choice = i
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
    
# Finding out which spots in our maze is the best according to our trained data    
def decideBestHidingSpot(maze, agent, model):
    global widthLength
    mazeList = list(maze)
    i = 0
    dataList = []
    dataListICorrespondent = []
    predictedList = {}
    while i < len(mazeList):
        # Use this 
        if widthLength<i and i < len(mazeList)-widthLength and i % widthLength != 0  and (i+2) % widthLength != 0 and (mazeList[i] == " " ):
            dataList.append(wallsAround(maze,i))
            dataList.append(stepsFromEntranceFunc(maze,i))
            dataList.append(pathDecisionChoicesFromEntranceFun(maze,i))
            dataListICorrespondent.append(i)
        i = i + 1
    dataList = np.reshape(dataList, (-1, 3))
    dataList = preprocessing.StandardScaler().fit(dataList).transform(dataList)
    y_pred = model.predict(dataList)
    #maxPos = np.where(y_pred == np.amax(y_pred))
    #aInteger = ",".join(maxPos[0])
    i = 0
    location = agent.currentLocation
    # finding the largest prediction
    for prediction in y_pred:
        if prediction == np.amax(y_pred):
            location = dataListICorrespondent[i]
        i = i + 1
    #print(y_pred)
    #print(np.amax(y_pred))
    #print(location)
    return location
    
# Traverse function for the hider to discover spots and hide
def discoveryHiderTraverse(maze, agent, model):
    global hiderSteps
    global rounds
    global allAvailableSpaces
    mazeList = list(maze)
    i = 0
    choices = 0
    choicesList = [-1,-1,-1,-1]
    while i < len(mazeList) and mazeList[i] != agent.name:
        i = i + 1
    agent = whatIsAvailable(maze,agent)
    agent.spotsSeeing.clear()
    updateSight(mazeList,agent,i)
    #print("agent path = "+str(agent.path))
    #print("agent location = "+str(agent.currentLocation))
    allAvailableSpacesby10 = allAvailableSpaces / 10
    # checking to see if we know enough spots to determine where to hider
    if agent.path == [] and ((100 * (rounds+1) <= int(spotsKnown(agent.maze))) or (int(spotsKnown(agent.maze))+allAvailableSpacesby10 >= allAvailableSpaces) or (hiderSteps > maxHiderSteps - 25)):
        agent.path = uniformCostPath(list(agent.maze), agent.currentLocation, decideBestHidingSpot(agent.maze,agent, model))
    #decideBestHidingSpot(agent.maze,agent, model)
    
    # making sure we haven't reached the end of our path if the agent has one
    if agent.path != [] and agent.currentLocation == agent.path[len(agent.path)-1].location:
            hiderSteps = maxHiderSteps
            agent.path = []
    # if our agent has a path then that's our first priority for a means of traversing
    if agent.path != []:
        for spot in agent.path:
            if spot.location == i:
                index = agent.path.index(spot)
                choice = agent.path[index+1]
                break
        try:
            choice = choice.location
        except:
            print("HEREERERE")
            agent.path = []
            choice = i
    # otherwise, traverse backwards if no new random spots available until one is found
    elif checkForNewSpot(maze,agent) == 0:
        choice = randomTraverseBackwards(agent,i)
        if choice == 51:
            agent.maze = maze
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
    hiderSteps = hiderSteps + 1
    
    #agent.wallsAround(maze)
    #if agent.wallsAroundAgent == 3:
     #   hiderSteps = maxHiderSteps
    if maxHiderSteps <= hiderSteps: 
        agent.stepsFromEntrance = stepsFromEntranceFunc(maze,agent.currentLocation)
        agent.wallsAroundAgent = wallsAround(maze,agent.currentLocation)
        agent.pathDecisionChoicesFromEntrance = pathDecisionChoicesFromEntranceFun(maze,agent.currentLocation)
        #print("walls around agent = "+str(agent.wallsAroundAgent))
        #print("steps from entrance = "+str(agent.stepsFromEntrance))
        #print("path decision choices from entrance = "+str(agent.pathDecisionChoicesFromEntrance))
    updateSight(mazeList,agent,choice) #debugging purposes (so we can see what he's seeing with the print)
    return maze

# looks for a new path above the agent
def topPath(mazeList,agent,currentLocation):
    global widthLength
    if (currentLocation - (widthLength*2)-1) <= 0:
        return -1
    if mazeList[currentLocation-widthLength] != " ":
        return -1
    i = currentLocation - widthLength
    # checking to see if the space to the left of you is a space and the space right above it (past the line of walls) so we can
    # expand the view of the agent to the proper length of the maze halls
    left = True
    right = True
    leftBound = False
    rightBound = False
    # here we make sure the spaces to the left or right are empty along with the ones right above so we can
    # use this line of sight. If there is something obstructing right here then we don't even expand this way
    #if (mazeList[currentLocation-1] != " " and mazeList[currentLocation-1] != "1" and mazeList[currentLocation-1] != "0") and (mazeList[(currentLocation-(widthLength))-1] != " " and mazeList[(currentLocation-(widthLength))-1] != "1" and mazeList[(currentLocation-(widthLength))-1] != "0"):
    if mazeList[currentLocation-1] != " " and mazeList[currentLocation-widthLength-1] != " ":
        leftBound = True
    #if (mazeList[currentLocation+1] != " " and mazeList[currentLocation+1] != "1" and mazeList[currentLocation+1] != "0") and (mazeList[(currentLocation-(widthLength))+1] != " " and mazeList[(currentLocation-(widthLength))+1] != "1" and mazeList[(currentLocation-(widthLength))+1] != "0"):
    if mazeList[currentLocation+1] != " " and mazeList[currentLocation-widthLength+1] != " ":    
        rightBound = True
        
    if left == True:
        i = currentLocation - widthLength
        while 0 < i:
            if mazeList[i] != " " and mazeList[i] != "1" and mazeList[i] != "0":
                break
            # if there is a path to the left above
            if leftBound:
                if mazeList[i-1] == " " and i-1 not in agent.spotsVisited:
                    return i-1
            else:
                if mazeList[i-2] == " " and i-2 not in agent.spotsVisited:
                    return i-2
            # if mazeList[i-1] == " " or mazeList[i-1] == "1"  or mazeList[i-1] == "0":
                # agent.addSpotSeeing(mazeList,i-1)
            i = i - widthLength
        # if there is a path to the left above the 
        if leftBound:
            if mazeList[i-1] == " " and i-1 not in agent.spotsVisited:
                return i-1
        else:
            if mazeList[i-2] == " " and i-2 not in agent.spotsVisited:
                return i-2
    # we do the same with the right side
    if right == True:
        i = currentLocation - widthLength
        while 0 < i:
            if mazeList[i] != " " and mazeList[i] != "1" and mazeList[i] != "0":
                break
            # if there is a path to the right above 
            if rightBound:
                if mazeList[i+1] == " " and i+1 not in agent.spotsVisited:
                    return i+1
            else:
                if mazeList[i+2] == " " and i+2 not in agent.spotsVisited:
                    return i+2
            #if mazeList[i+1] == " " or mazeList[i+1] == "1" or mazeList[i+1] == "0":
            #    agent.addSpotSeeing(mazeList,i+1)
            i = i - widthLength
        if rightBound:
            if mazeList[i+1] == " " and i+1 not in agent.spotsVisited:
                return i+1
        else:
            if mazeList[i+2] == " " and i+2 not in agent.spotsVisited:
                return i+2
    return -1

# looks for a new path below the agent
def bottomPath(mazeList,agent,currentLocation):
    global widthLength
    if len(mazeList) < (currentLocation + (widthLength*2)+1):
        return -1
    if mazeList[currentLocation+widthLength] != " ":
        return -1
    i = currentLocation + widthLength
    # checking to see if the space to the left of you is a space and the space right above it (past the line of walls) so we can
    # expand the view of the agent to the proper length of the maze halls
    left = True
    right = True
    leftBound = False
    rightBound = False
    #if (mazeList[currentLocation-1] != " " and mazeList[currentLocation-1] != "1" and mazeList[currentLocation-1] != "0") and (mazeList[(currentLocation+(widthLength))-1] != " " and mazeList[(currentLocation+(widthLength))-1] != "1"and mazeList[(currentLocation+(widthLength))-1] != "0"):
    if mazeList[currentLocation-1] != " " and mazeList[currentLocation+widthLength-1] != " ":    
        leftBound = True
    #if (mazeList[currentLocation+1] != " " and mazeList[currentLocation+1] != "1" and mazeList[currentLocation+1] != "0") and (mazeList[(currentLocation+(widthLength))+1] != " " and mazeList[(currentLocation+(widthLength))+1] != "1" and mazeList[(currentLocation+(widthLength))+1] != "0"):
    if mazeList[currentLocation+1] != " " and mazeList[currentLocation+widthLength+1] != " ":        
        rightBound = True
        
    if left == True:
        i = currentLocation + widthLength
        while i < len(mazeList)-1:
            if mazeList[i] != " " and mazeList[i] != "1" and mazeList[i] != "0":
                break
            # if there is a path to the left below  
            if leftBound:
                if mazeList[i - 1] == " " and i - 1 not in agent.spotsVisited:
                    return i - 1
            else:
                if mazeList[i-2] == " " and i-2 not in agent.spotsVisited:
                    return i-2
            #if mazeList[i-1] == " " or mazeList[i-1] == "1" or mazeList[i-1] == "0":
            #    agent.addSpotSeeing(mazeList,i-1)
            i = i + widthLength
        # if there is a path to the left below 
        if leftBound:
            if mazeList[i-1] == " " and i-1 not in agent.spotsVisited:
                return i-1
        else:
            if mazeList[i-2] == " " and i-2 not in agent.spotsVisited:
                return i-2
            
    if right == True:
        i = currentLocation + widthLength
        while i < len(mazeList)-1:
            if mazeList[i] != " " and mazeList[i] != "1" and mazeList[i] != "0":
                break
            # if there is a path to the right below  
            if rightBound:
                if mazeList[i+1] == " " and i+1 not in agent.spotsVisited:
                    return i+1
            else:
                if mazeList[i+2] == " " and i+2 not in agent.spotsVisited:
                    return i+2
            #if mazeList[i+1] == " " or mazeList[i+1] == "1" or mazeList[i+1] == "0":
            #    agent.addSpotSeeing(mazeList,i+1)
            i = i + widthLength
        # if there is a path to the right below
        if rightBound:  
            if mazeList[i+1] == " " and i+1 not in agent.spotsVisited:
                return i+1
        else:
            if mazeList[i+2] == " " and i+2 not in agent.spotsVisited:
                return i+2
    return -1

# looks for a path to the left of the agent
def leftPath(mazeList,agent,currentLocation):
    if mazeList[currentLocation-1] != " " or mazeList[currentLocation-2] != " ":
        return -1
    global widthLength
    i = currentLocation - 1
    top = True
    bottom = True
    #if (mazeList[currentLocation-widthLength] != " " and mazeList[currentLocation-widthLength] != "1" and mazeList[currentLocation-widthLength] != "0") and (mazeList[(currentLocation-(widthLength))-1] != " " and mazeList[(currentLocation-(widthLength))-1] != "1"and mazeList[(currentLocation-(widthLength))-1] != "0"):
    #    top = False
    #if (mazeList[currentLocation+widthLength] != " " and mazeList[currentLocation+widthLength] != "1" and mazeList[currentLocation+widthLength] != "0") and (mazeList[(currentLocation+(widthLength))-1] != " " and mazeList[(currentLocation+(widthLength))-1] != "1" and mazeList[(currentLocation+(widthLength))-1] != "0"):
    #    bottom = False
        
    if top == True:
        i = currentLocation - 1
        while mazeList[i] != "|" and mazeList[i] != "+" and mazeList[i] != "-":
            if mazeList[i] != " " and mazeList[i] != "1" and mazeList[i] != "0":
                break
            # if there is a path on the top of the left side
            if mazeList[i-widthLength] == " " and i-widthLength not in agent.spotsVisited:
                if mazeList[i-widthLength-widthLength] == "~" or mazeList[i-widthLength-1] == "~":
                    return i-widthLength
            # possibly delete
            #if mazeList[i-widthLength] == " " or mazeList[i-widthLength] == "1" or mazeList[i-widthLength] == "0":
             #   agent.addSpotSeeing(i-widthLength)
            #    agent.addSpotSeen(i-widthLength)
            i = i - 1
        if mazeList[i-widthLength] == " " and i-widthLength not in agent.spotsVisited:
            if mazeList[i-widthLength-widthLength] == "~" or mazeList[i-widthLength-1] == "~":
                return i-widthLength
    if bottom == True:
        i = currentLocation - 1
        while mazeList[i] != "|" and mazeList[i] != "+" and mazeList[i] != "-":
            if mazeList[i] != " " and mazeList[i] != "1" and mazeList[i] != "0":
                break
            # if there is a path on the bottom of the left side
            if mazeList[i+widthLength] == " " and i+widthLength not in agent.spotsVisited:
                if mazeList[i+widthLength+widthLength] == "~" or mazeList[i+widthLength-1] == "~":
                    return i+widthLength
            #if mazeList[i+widthLength] == " " or mazeList[i+widthLength] == "1" or mazeList[i+widthLength] == "0":
            #    agent.addSpotSeeing(i+widthLength)
            #    agent.addSpotSeen(i+widthLength)
            i = i - 1
        if mazeList[i+widthLength] == " " and i+widthLength not in agent.spotsVisited:
            if mazeList[i+widthLength+widthLength] == "~" or mazeList[i+widthLength-1] == "~":
                return i+widthLength
    return -1

# looks for paths to the right of the agent
def rightPath(mazeList,agent,currentLocation):
    if mazeList[currentLocation+1] != " " or mazeList[currentLocation+2] != " ":
        return -1
    global widthLength
    i = currentLocation + 1
    top = True
    bottom = True
    #if (mazeList[currentLocation-widthLength] != " " and mazeList[currentLocation-widthLength] != "1" and mazeList[currentLocation-widthLength] != "0") and (mazeList[(currentLocation-(widthLength))+1] != " " and mazeList[(currentLocation-(widthLength))+1] != "1"and mazeList[(currentLocation-(widthLength))+1] != "0"):
    #    top = False
    #if (mazeList[currentLocation+widthLength] != " " and mazeList[currentLocation+widthLength] != "1" and mazeList[currentLocation+widthLength] != "0") and (mazeList[(currentLocation+(widthLength))+1] != " " and mazeList[(currentLocation+(widthLength))+1] != "1" and mazeList[(currentLocation+(widthLength))+1] != "0"):
    #    bottom = False
    #agent.addSpotSeen(i) # so further path decision making can be made
    if top == True:
        i = currentLocation+ 1
        while mazeList[i] != "|"and mazeList[i] != "+" and mazeList[i] != "-":
            if mazeList[i] != " " and mazeList[i] != "1" and mazeList[i] != "0":
                break
            # if there is a path on the top of the right side
            if mazeList[i - widthLength ] == " " and i - widthLength not in agent.spotsVisited:
                if mazeList[i-widthLength-widthLength] == "~" or mazeList[i-widthLength+1] == "~":
                    return i - widthLength
            # possibly delete
            #if mazeList[i-widthLength] == " " or mazeList[i-widthLength] == "1" or mazeList[i-widthLength] == "0":
            #    agent.addSpotSeeing(i-widthLength)
             #   agent.addSpotSeen(i-widthLength)
            i = i + 1
        if mazeList[i - widthLength] == " " and i - widthLength not in agent.spotsVisited:
            if mazeList[i-widthLength-widthLength] == "~" or mazeList[i-widthLength+1] == "~":
                return i - widthLength
    if bottom == True:
        i = currentLocation + 1
        while mazeList[i] != "|" and mazeList[i] != "+" and mazeList[i] != "-":
            if mazeList[i] != " " and mazeList[i] != "1" and mazeList[i] != "0":
                break
            # if there is a path on the bottom of the right side
            if mazeList[i + widthLength] == " " and i + widthLength not in agent.spotsVisited:
                if mazeList[i+widthLength+widthLength] == "~" or mazeList[i+widthLength+1] == "~":
                    return i + widthLength
            #if mazeList[i+widthLength] == " " or mazeList[i+widthLength] == "1" or mazeList[i+widthLength] == "0":
             #   agent.addSpotSeeing(i+widthLength)
             #   agent.addSpotSeen(i+widthLength)
            i = i + 1
        if mazeList[i+ widthLength] == " " and i+ widthLength not in agent.spotsVisited:
            if mazeList[i+widthLength+widthLength] == "~" or mazeList[i+widthLength+1] == "~":
                return i+ widthLength
    return -1

# checks for a new unvisited spot for an agent to move to
def checkForNewPath(agent):
    global widthLength
    mazeList = list(agent.maze)
    choice = -1
    choices = 0
    choicesList = [-1,-1,-1,-1]
    #finding out where we need to look
    if agent.top != -1 and topPath(agent.maze, agent, agent.currentLocation) != -1:
        choicesList[choices] = topPath(agent.maze, agent, agent.currentLocation)
        print("top path chosen at "+str(choicesList[choices]))
        choices = choices + 1
    if agent.left != -1 and leftPath(agent.maze, agent, agent.currentLocation) != -1:
        choicesList[choices] = leftPath(agent.maze, agent, agent.currentLocation)
        print("left path chosen at "+str(choicesList[choices]))
        choices = choices + 1
    if agent.right != -1 and rightPath(agent.maze, agent, agent.currentLocation) != -1:
        choicesList[choices] = rightPath(agent.maze, agent, agent.currentLocation)
        print("right path chosen at "+str(choicesList[choices]))
        choices = choices + 1
    if agent.bottom != -1 and bottomPath(agent.maze, agent, agent.currentLocation) != -1:
        choicesList[choices] = bottomPath(agent.maze, agent, agent.currentLocation)
        print("bottom path chosen at "+str(choicesList[choices]))
        choices = choices + 1
    print(choicesList)
    if 0 < choices:
        choicesList = choicesList[:choices]
        choice = random.sample(choicesList,1)
        choice = choice[0]
        print("going with "+str(choice))
    if choice != -1:
        agent.path = uniformCostPath(list(agent.maze), agent.currentLocation, choice)
    return choice
    
# Returns list of unexplored spaces    
def findUnexploredNewSpaces(maze, agent):
    global widthLength
    unexploredSpaces = []
    result = []
    count = 0
    minn = 50000
    mazeList = list(maze)
    for space in mazeList:
        if space == " ":
            if mazeList[count + 1] == "~" or mazeList[count-1] == "~" or mazeList[count+widthLength] == "~" or mazeList[count-widthLength] == "~":
                unexploredSpaces.append(count)
        count = count + 1
    for spot in unexploredSpaces:
        tempList = uniformCostPath(list(agent.maze), agent.currentLocation, spot)
        if len(tempList) < minn:
            minn = len(tempList)
            result = tempList
    for i in result:
        print("I LOCATION = "+str(i.location))
    agent.path = result
    return result
    
# Performs a decision made search until it finds the hiding agent, then it will use uniform cost searching algorithm to find the best path to the hiders last known location    
def randomTraverseDecisionMaking(maze, agent):
    global stepsTaken
    mazeList = list(maze)
    i = 0
    pathCheck = -1
    choice = -1
    choices = 0
    choicesList = [-1,-1,-1,-1]
    while i < len(mazeList) and mazeList[i] != agent.name:
        i = i + 1
    agent = whatIsAvailable(maze,agent)
    agent.spotsSeeing.clear()
    updateSight(mazeList,agent,i)
    checkForHiderSight(mazeList,agent)
    #newSpaces = findUnexploredNewSpaces(agent.maze,agent)
    # making sure we haven't reached the end of our path if the agent has one
    if agent.path != [] and agent.currentLocation == agent.path[len(agent.path)-1].location:
            agent.path = []
    # if we have an empty path, let's update to a possible new path available
    if agent.path == [] and agent.currentLocation != -1 and 0 < stepsTaken:
        pathCheck = checkForNewPath(agent)
    # if we have an empty path, let's update to a possible new path available with all unexplored spaces
    if agent.path == [] and agent.currentLocation != -1 and 0 < stepsTaken:
        newSpaces = findUnexploredNewSpaces(agent.maze,agent)
    # if our agent has a path then that's our first priority for a means of traversing
    if agent.path != []:
        print("TRAVERSING PATH")
        for spot in agent.path:
            print(str(spot.location))
        for spot in agent.path:
            #print("sooo"+str(spot.location))
            if spot.location == i:
                index = agent.path.index(spot)
                choice = agent.path[index+1]
                break
        choice = choice.location
    # otherwise, traverse backwards if no new paths are available until one is found
    #elif checkForNewSpot(maze,agent) == 0:
    elif 1 < stepsTaken and pathCheck == -1:
        print("TRAVERSING BACKWARDS")
        choice = randomTraverseBackwards(agent,i)
    # else we choose a random path by gathering what's available 
    #else:
    if choice == -1:
        print("TRAVERSING RANDOM")
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
    seeker = Agent("0",-1,-1,-1,-1,-1,-1,-1,-1,-1,[],[],[],[],maze) #(name,top,bottom,left,right,currentLocation,opposingAgentLastLocation,wallsAroundAgent,stepsFromEntrance,pathDecisionChoicesFromEntrance,spotsVisited,spotsSeen,spotsSeeing,path,mazeList)
    hider = Agent("1",-1,-1,-1,-1,-1,-1,-1,-1,-1,[],[],[],[],maze)
    #maze = add_agent(maze, seeker)
    maze = add_agent(maze,hider)
    updateSight(list(maze),seeker,seeker.currentLocation)
    allAvailableSpaces = spotsKnown(maze)
    stepsTakenPerRound = []
    #testing = uniformCostPath(list(maze),seeker.currentLocation,hider.currentLocation)
    
    # loading machine learning trained data
    df = pd.read_csv("data-example.csv")
    cdf = df[['Walls Around Agent','Steps From Entrance','Path Decision Choices From Entrance','Steps Taken']]

    # creating training dataset
    msk = np.random.rand(len(df)) < 0.8
    train = cdf[msk]
    test = cdf[~msk]

    # creating model
    model = linear_model.LinearRegression()
    #model = LogisticRegression(C=0.01, solver='liblinear')
    #model = DecisionTreeClassifier(criterion="entropy", max_depth = 3)

    # setting up labels/features
    X_train = np.asanyarray(train[['Walls Around Agent','Steps From Entrance','Path Decision Choices From Entrance']])
    X_train = preprocessing.StandardScaler().fit(X_train).transform(X_train)
    y_train = np.asanyarray(train[['Steps Taken']])
    #X_test = np.asanyarray(test[['Walls Around Agent','Steps From Entrance','Path Decision Choices From Entrance']])
    #X_test = preprocessing.StandardScaler().fit(X_test).transform(X_test)
    #y_test = np.asanyarray(test['Steps Taken'])
    
    # fitting the model
    model.fit (X_train, y_train)
    
    # running the game
    while gameComplete == 0:
        if hiderSteps < maxHiderSteps:
            if hiderHiding == 1:
                hiderHiding = 0
            maze = discoveryHiderTraverse(maze,hider,model)
            print("HIDING AGENT MAZE = ")
            print(hider.maze)
            print("top = "+str(hider.top)+"\nbottom = "+str(hider.bottom)+"\nleft= "+str(hider.left)+"\nright = "+str(hider.right)+"\n")
            print(maze)
            #print("spots known = "+str(spotsKnown(hider.maze)))
        else:
            if hiderHiding == 0:
                maze = add_agent(maze, seeker)
                hiderHiding = 1
        
            # Random search
            #maze = randomTraverse(maze,seeker)

            # Random search to new locations
            #maze = randomTraverseNewSpots(maze,seeker)

            # Random search to new locations with visual clues (deprecated, can get caught in a loop with current visual info; creating proper path to the hider with dijkstra/a* algos to fix this)
            #maze = randomTraverseNewSpotsSight(maze,seeker) 

            # Random search with uniform cost path seeking 
            maze = randomTraverseUniformCostSeek(maze,seeker) 

            # Random search with uniform cost path seeking + decision making
            #maze = randomTraverseDecisionMaking(maze,seeker) 
            
            print("AGENT MAZE = ")
            print(seeker.maze)
            print("top = "+str(seeker.top)+"\nbottom = "+str(seeker.bottom)+"\nleft= "+str(seeker.left)+"\nright = "+str(seeker.right)+"\n")
            print(maze)
            if gameComplete == 1:
                stepsTakenPerRound.append(stepsTaken)
                rounds = rounds + 1
                if rounds < 5:
                    gameComplete = 0
                    stepsTaken = 0
                    hiderSteps = 0
                    seeker = Agent("0",-1,-1,-1,-1,-1,-1,-1,-1,-1,[],[],[],[],maze) 
                    maze = remove_seeker(maze)
        # if you press a key it slows down the simulation
        # This only works on Windows        
        # if msvcrt.kbhit():
           # key_stroke = msvcrt.getch()
           # print(key_stroke)
           # if slowDown == 0:
               # slowDown = 1
           # else:
               # slowDown = 0
        #if slowDown == 0:
        #    time.sleep(0.06)
        #else:
        #    time.sleep(0.6) # replace with putting this(traverse/keyboardinput)^ in tick from game engine and prints in render(or actual 3d maze)
        
        #print("SEEKER CURRENT LOCATION = "+str(seeker.currentLocation))
        #testing = uniformCostPath(list(seeker.maze),seeker.currentLocation,57)
        #for test in testing:
        #    print("UNIFORM COST PATH = "+str(test.location))
        #break
    #print("Steps Taken = "+str(stepsTaken))
    #print("walls around agent = "+str(hider.wallsAroundAgent))
    #print("steps from entrance = "+str(hider.stepsFromEntrance))
    #print("path decision choices from entrance = "+str(hider.pathDecisionChoicesFromEntrance))
    count = 0
    for steps in stepsTakenPerRound:
        print(str(steps)+" steps in round "+str(count+1))
        count = count + 1
    
    #with open('data-example.csv', 'a') as fd:  
    #    fd.write(str(hider.wallsAroundAgent)+","+str(hider.stepsFromEntrance)+","+str(hider.pathDecisionChoicesFromEntrance)+","+str(stepsTaken)+str("\n"))
    #print("Spots Visited = "+str(seeker.spotsVisited))
    #print("Current Location = "+str(seeker.currentLocation))
