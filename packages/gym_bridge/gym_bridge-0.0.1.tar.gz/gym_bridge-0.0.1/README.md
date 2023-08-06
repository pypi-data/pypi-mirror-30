# Gym Bridge
Gym environment for navigating across a bridge on a frozen lake.

## Installation
1. Clone the repo
2. Run `python setup.py install`

## Usage
```python
import gym
import gym_bridge
import time

env = gym.make('bridge-v0')
for i_episode in range(20):
    observation = env.reset()
    for t in range(100):
        env.render()
        print(observation)
        action = env.action_space.sample()
        observation, reward, done, info = env.step(action)
        if done:
            print("Episode finished after {} timesteps".format(t+1))
            break
        time.sleep(0.04)

env.render()
```
