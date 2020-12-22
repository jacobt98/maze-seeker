# maze-seeker
Repository for Artificial Intelligence - Group 5. We will be implementing a hide and seek game with autonomous agents for both hiding and seeking.

Colab Link (runnable through browser): https://colab.research.google.com/drive/1xuN9cMv6ZWHNe_A8w8h7459hFEBe7uCO?usp=sharing

```
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
|        |                 |  |           |     |
+  +--+  +  +--+--+--+--+  +  +  +  +--+  +--+  +
|  |        |     |        |     |  |  |     |  |
+  +--+--+--+  +  +  +--+--+  +--+  +  +--+  +  +
|        |     |  |  |        |     |           |
+--+--+  +  +--+  +  +--+--+--+  +--+--+--+--+  +
|     |  |     |  |  |        |        |     |  |
+  +  +  +--+  +  +  +  +--+  +--+--+  +  +  +  +
|  |     |     |  |     |  |        |     |  |  |
+  +--+  +  +--+  +--+--+  +--+--+  +  +--+  +  +
|  |     |  |  |     |        |     |     |  |  |
+  +--+--+  +  +--+--+  +--+--+  +--+--+--+  +  +
|  |     |  |        |           |           |  |
+  +  +  +  +  +  +--+  +--+--+--+--+  +--+--+  +
|     |     |  |                       |      01|
+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+--+
```

In this program, we created a maze and represent it through a string in Python, and then place two autonomous agents, a hiding agent '1' and a seeking agent '0', into the maze by replacing a blank space for which they make up. The hiding agent is given a limited number of steps before the seeking agent begins to search the maze for him and when the hiding agent gets close to this number, the agent will use machine learning to establish the best possible hiding spot given the spots he knows. To do this, we did tests and gathered data on the 'Walls Around Agent', 'Steps From Entrance', 'Path Decisions Made From Entrance', and the 'Steps Taken' (as the label) when the seeking agent found the hiding agent to have correlated features which would work well with a linear regression model. Using this model, the hiding agent can predict (without overfitting/underfitting) which spot will take the most amount of steps and begin to make it's way to that location using uniform cost algorithms to easily find the quickest path. When the seeking agent begins to search for the hiding agent, the hiding agent is not allowed to move and remains in that location even after found which leads to the round being over. When this happens, we remove the seeking agent, and let the hiding agent continue to find more locations until they reach the certain number of steps that allow for the seeker to search again. We do this for 5 rounds, and as the hiding agent is given more knowledge on the maze and available locations to hide in, the number of steps taken from the seeker to find the hider tends to go up as one would expect. Below is some examples which show how long it takes for the seeker to find the hider when they have a completely random traverse method, have some location retention, and then when the hiding agent is given the ability to make a hiding spot decision based on the machine learning implementation. The completely random traverse method takes an absurd amount of steps, the seeking agent having location retention gives a substantial improvement on the steps taken, while the hiding agent being able to decide where to hide requires more steps from the seeker as expected. 

# Random Algorithm
```
Steps Taken = 68925
```

# Location Retention
```
Steps Taken = 544
```

# Machine Learning
```
Steps taken = 660
```
