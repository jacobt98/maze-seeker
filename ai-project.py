import random
from random import shuffle, randrange

# Agent class that contains all the information needed for our agents
class Agent:
    def __init__(self,name,top,bottom,left,right):
        self.name = name
        self.top = top
        self.bottom = bottom
        self.right = right
        self.left = left

width = 16 # width of maze
height = 8 # height of maze
widthLength = ((width*3)+2) # length of the string width including \n and wall (50)
#(*3 because "|  " and "+--"; +2 because \n and wall) use less space("+-") to make it *2
gameComplete = 0 # used to loop the program until the game is complete
stepsTaken = 0 # count how many steps taken until the seeker finds the hider

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
    return maze

# adds agent to a spot with a given location (be careful)
def add_agent_spot(maze,agent,spot):
    mazeList = list(maze)
    mazeList[spot] = agent.name
    maze = "".join(mazeList)
    agent = whatIsAvailable(maze,agent)
    return maze

# just finds a random spot scanning from right to left, bottom to top
def add_agent_random_spot(maze,agent):
    mazeList = list(maze)
    i = len(mazeList)-1
    gettingSpot=0
    while gettingSpot == 0:
        if i <= 0:
            i = len(mazeList)-1
        i = i - 1
        if mazeList[i] == " " and 30 < randrange(32):
            gettingSpot=1
    mazeList[i] = agent.name
    maze = "".join(mazeList)
    agent = whatIsAvailable(maze,agent)
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
    if mazeList[i-widthLength] == "1":# widthLength = 50
        gameComplete = 1
    if mazeList[i-1] == "1":
        gameComplete = 1
    if mazeList[i+1] == "1":
        gameComplete = 1
    if mazeList[i+widthLength] == "1":
        gameComplete = 1

# looks around the agent for " " and updates it's data accordingly
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
        choicesList[choices] = agent.top #mazeList[agent.top] = agent.name
        choices = choices + 1
    if agent.bottom != -1:
        choicesList[choices] = agent.bottom #mazeList[agent.bottom] = agent.name
        choices = choices + 1
    if agent.left != -1:
        choicesList[choices] = agent.left #mazeList[agent.left] = agent.name
        choices = choices + 1
    if agent.right != -1:
        choicesList[choices] = agent.right #mazeList[agent.right] = agent.name
        choices = choices + 1

    choicesList = choicesList[:choices]
    #print(choicesList)
    choice = random.sample(choicesList,1)
    choice = choice[0]
    mazeList[choice] = agent.name
    agent = agent_reset(agent)
    maze = "".join(mazeList)
    agent = whatIsAvailable(maze,agent)
    stepsTaken = stepsTaken + 1
    return maze

# main
if __name__ == '__main__':
    maze = make_maze()
    #maze = make_entrance(maze)
    seeker = Agent("0",-1,-1,-1,-1)
    hider = Agent("1",-1,-1,-1,-1)
    maze = add_agent(maze, seeker)
    maze = add_agent_random_spot(maze,hider)
    while gameComplete == 0:
        maze = randomTraverse(maze,seeker)
        print("top = "+str(seeker.top)+"\nbottom = "+str(seeker.bottom)+"\nleft= "+str(seeker.left)+"\nright = "+str(seeker.right)+"\n")
        print(maze)
    print("Steps Taken = "+str(stepsTaken))
