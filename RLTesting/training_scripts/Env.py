import gymnasium as gym


class EnvWrapper(gym.Env):
    def __init__(self):
        self.env = gym.make('FrozenLake-v1', map_name="4x4", is_slippery=False, max_episode_steps=200,
                            render_mode="rgb_array")
        # self.env = gym.make('FrozenLake-v1', desc=None, map_name="4x4", is_slippery=False, max_episode_steps = 20)
        # self.env = gym.make("CartPole-v1", max_episode_steps=200)
        self.action_space = self.env.action_space
        self.observation_space = self.env.observation_space
        self.rewarded_actions = {}
        self.current_state = 0

    def render(self, mode='human'):
        return self.env.render()

    def step(self, action):
        obs, reward, terminated, truncated, info = self.env.step(action)  # calls the gym env methods
        if self.current_state in self.rewarded_actions:
            if action == self.rewarded_actions[self.current_state]:
                # if obs == 15:
                #     reward = 5
                # else:
                    reward = 1
            else:
                reward = -1
        elif obs == 15:
            reward = 5
        elif terminated:
            reward = -3
        else:
            reward = -1
        self.current_state = obs
        return obs, reward, terminated, truncated, info

    def reset(self, seed=None):
        obs = self.env.reset(seed=seed)
        self.current_state = obs[0]
        return obs

    def set_rewarded_actions(self, rewarded_actions):
        self.rewarded_actions = rewarded_actions
        return

    def set_current_state(self, current_state):
        self.current_state = current_state
        return

    @property
    def P(self):
        return self.env.P

    @property
    def desc(self):
        return self.env.desc


if __name__ == "__main__":
    env = EnvWrapper()
    env.reset()
    env.render(mode='rgb_array')
    observation, info = env.reset()
    for _ in range(10):

        action = env.action_space.sample()  # agent policy that uses the observation and info
        observation, reward, terminated, truncated, info = env.step(action)
        if terminated or truncated:
            observation, info = env.reset()
    env.close()
