import gymnasium as gym

class EnvWrapper(gym.Env):
    def __init__(self):
        self.env = gym.make('FrozenLake-v1', map_name="4x4", is_slippery=False, max_episode_steps = 200, render_mode="human")
        # self.env = gym.make('FrozenLake-v1', desc=None, map_name="4x4", is_slippery=False, max_episode_steps = 20)
        # self.env = gym.make("CartPole-v1", max_episode_steps=200)
        self.action_space = self.env.action_space
        self.observation_space = self.env.observation_space

    def render(self, mode='human'):
        return self.env.render()
    
    def step(self, action):
        obs, reward, terminated, truncated, info = self.env.step(action)   # calls the gym env methods
        if obs == 15:
            reward = 1
        elif terminated:
            reward = -10
        else:
            reward = -1
        return obs, reward, terminated, truncated, info

    def reset(self, seed=None):
        return self.env.reset(seed=seed)
    
    def randomlize_rewarder():
        return


if __name__ == "__main__":
    env = EnvWrapper()
    env.reset()
    env.render(mode='human')
    observation, info = env.reset()
    for _ in range(10):

        action = env.action_space.sample()  # agent policy that uses the observation and info
        observation, reward, terminated, truncated, info = env.step(action)
        if terminated or truncated:
            observation, info = env.reset()
    env.close()