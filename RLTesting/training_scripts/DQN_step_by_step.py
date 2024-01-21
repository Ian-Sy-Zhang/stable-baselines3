import gymnasium as gym
from stable_baselines3 import DQN
from stable_baselines3.common.vec_env import DummyVecEnv
from Env import EnvWrapper
from stable_baselines3.common.logger import configure


# 创建一个游戏环境，例如CartPole
env = EnvWrapper()
env.reset()


# 初始化DQN模型
model = DQN("MlpPolicy", env, verbose=1, batch_size=1)
new_logger = configure(folder="logs", format_strings=["stdout", "log", "csv", "tensorboard"])
model.set_logger(new_logger)

vec_env = model.get_env()
obs = vec_env.reset()
vec_env.render(mode='human')

# 设定最大步数
max_steps = 10000

# 训练循环
for step in range(max_steps):
    # 选择一个动作
    action, _states = model.predict(obs, deterministic=True)

    # 环境执行动作
    new_obs, reward, done, info = vec_env.step(action)

    # 存储新的转换到回放缓冲区
    model.replay_buffer.add(obs, action, new_obs, reward, done, info)

    # 检查回放缓冲区是否有足够的数据来进行学习
    if model.replay_buffer.size() > model.batch_size:
        # 执行一步学习
        model.train(gradient_steps=1)

    # 将新的观察结果设置为下一步的初始状态
    obs = new_obs

    # 检查是否结束
    if done:
        # 重置环境状态
        obs = env.reset()

# 保存模型
model.save("dqn_cartpole")

# 关闭环境
env.close()