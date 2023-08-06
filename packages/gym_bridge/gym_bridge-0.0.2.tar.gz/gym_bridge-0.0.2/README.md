# Gym Bridge
Gym environment for navigating across an ice bridge on a frozen lake.

Creates a map that looks like:
```
  SFFFFFHFFFFFF
  FFFFFFHFFFFFF
  FFFFFFHFFFFFF
  FFFFFFHFFFFFF
  FFFFFFHFFFFFF
  FFFFFFFFFFFFF
  FFFFFFHFFFFFF
  FFFFFFHFFFFFF
  FFFFFFHFFFFFF
  FFFFFFHFFFFFF
  FFFFFFHFFFFFG
```
Where `S` is the start postion and `G` is the goal. Spaces marked `F` are frozen lake, while `H` are holes.
The start position, goal position, and gate/bridge position are randomly initialized on environment creation. 
The bridge will always be through the line of holes that divides the map in half, 
and the start and goal positions are always initialized on opposite sides of the bridge. 

You receive a reward of 1 for reaching the goal, 0 if otherwise.

## Installation
`pip install gym_bridge`

## Usage
```python
import gym
import gym_bridge

env = gym.make('bridge-v0')
for i_episode in range(20):
    observation = env.reset()
    for t in range(100):
        env.render()
        print(observation)

        # LEFT = 0, DOWN = 1, RIGHT = 2, UP = 3
        action = env.action_space.sample()  # Random action.

        observation, reward, done, info = env.step(action)
        if done:
            print("Episode finished after {} timesteps".format(t+1))
            break

env.render()
```
