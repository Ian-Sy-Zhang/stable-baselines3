import bug_lib as BL
import subprocess
import os
import sys

sys.path.insert(0, './training_scripts/')
from stable_baselines3 import DQN, PPO, A2C, SAC
from stable_baselines3.common.logger import configure
from stable_baselines3.common.callbacks import BaseCallback
from stable_baselines3.common.env_util import make_vec_env
import random
import numpy as np

import training_scripts.Env


class TerminateOnDoneCallback(BaseCallback):
    """
    自定义回调，用于在FrozenLake环境中检测终止状态并设置停止标志。
    """

    def __init__(self, env, verbose=0):
        super(TerminateOnDoneCallback, self).__init__(verbose)
        self.env = env

    def _on_step(self) -> bool:
        """
        在每个训练步骤结束时调用此方法。

        :return: (bool) 如果为False，则停止训练。
        """
        # 检查是否有任何环境实例被标记为done
        if self.env.envs[0].unwrapped.Done:
            # 在FrozenLake环境中，done为True意味着我们应该停止训练
            print(self.env.envs[0].state_action_pairs)
            self.env.envs[0].unwrapped.Done = False
            # self.state_action_pairs = []
            return False  # 这将不会立即停止训练，但会通知训练循环在下一个机会停止
        return True


def get_DQN_Model(env, model_path=os.path.join('RLTesting', 'logs', 'dqn.zip')):
    if os.path.isfile(model_path):
        print("loading existing model")
        model = DQN.load(model_path, env=env)
    else:
        print("creating new model")
        model = DQN("MlpPolicy", env, batch_size=4, learning_rate=0.025, learning_starts=0)
        new_logger = configure(folder="logs", format_strings=["stdout", "log", "csv", "tensorboard"])
        model.set_logger(new_logger)
    return model


def train_DQN_model(model, max_steps=80, model_path=os.path.join('RLTesting', 'logs', 'dqn.zip')):
    vec_env = model.get_env()
    obs = vec_env.reset()
    vec_env.render(mode='human')

    action_state_list = []

    for step in range(max_steps):
        # 选择一个动作
        action, _states = model.predict(obs)
        # action, _states = model.predict(obs, deterministic=True)

        # 环境执行动作
        new_obs, reward, done, info = vec_env.step(action)

        action_state_list.append(str(obs) + ',' + str(action) + ',' + str(reward))
        print("state, action:" + str(obs) + str(action))

        # 存储新转换到回放缓冲区
        model.replay_buffer.add(obs, new_obs, action, reward, done, info)

        # 检查回放缓冲区是否有足够的数据来进行学习
        if model.replay_buffer.size() > model.batch_size:
            # 执行一步学习
            model.train(gradient_steps=1)

        # 将新观察结果设置为下一步的初始状态
        obs = new_obs

        # 检查是否结束
        if done:
            # 重置环境状态
            obs = vec_env.reset()
            break

    # 保存模型
    model.save(model_path)

    vec_env.close()

    return action_state_list


def train_DQN_model_new(model, max_steps=80, model_path=os.path.join('RLTesting', 'logs', 'dqn.zip')):
    vec_env = model.get_env()
    vec_env.reset()
    vec_env.render()
    callback = TerminateOnDoneCallback(vec_env, verbose=1)
    model.learn(max_steps, callback=callback)
    action_state_list = vec_env.envs[0].get_state_action_pairs()
    model.save(model_path)
    vec_env.close()
    return action_state_list


def get_PPO_Model(env, model_path=os.path.join('RLTesting', 'logs', 'ppo.zip')):
    if os.path.isfile(model_path):
        print("loading existing model")
        model = PPO.load(model_path, env=env)
    else:
        print("creating new model")
        model = PPO('MlpPolicy', env, learning_rate=0.03, batch_size=4)
        # new_logger = configure(folder="logs", format_strings=["stdout", "log", "csv", "tensorboard"])
        # model.set_logger(new_logger)
    return model


def train_PPO_model(model, max_steps=80, model_path=os.path.join('RLTesting', 'logs', 'ppo.zip')):
    vec_env = model.get_env()
    vec_env.reset()
    vec_env.render()
    callback = TerminateOnDoneCallback(vec_env, verbose=1)
    model.learn(max_steps, callback=callback)
    action_state_list = vec_env.envs[0].get_state_action_pairs()
    # for step in range(max_steps):
    #     # 选择一个动作
    #     action, _states = model.predict(obs)
    #     # action, _states = model.predict(obs, deterministic=True)
    #
    #     # 环境执行动作
    #     new_obs, reward, done, info = vec_env.step(action)
    #
    #     action_state_list.append(str(obs) + ',' + str(action) + ',' + str(reward))
    #     print("state, action:" + str(obs) + str(action))
    #
    #     # 存储新转换到回放缓冲区
    #     model.rollout_buffer.add(obs, new_obs, action, reward, done, info)
    #
    #     # 将新观察结果设置为下一步的初始状态
    #     obs = new_obs
    #
    #     # 检查是否结束
    #     if done:
    #         # 本局游戏结束时进行训练
    #         model.train(gradient_steps=1)
    #         # 重置环境状态
    #         obs = vec_env.reset()
    #         break

    # 保存模型
    model.save(model_path)
    vec_env.close()
    return action_state_list


def get_A2C_Model(env, model_path=os.path.join('RLTesting', 'logs', 'a2c.zip')):
    if os.path.isfile(model_path):
        print("loading existing model")
        model = A2C.load(model_path, env=env)
    else:
        print("creating new model")
        model = A2C('MlpPolicy', env, verbose=1)
        # new_logger = configure(folder="logs", format_strings=["stdout", "log", "csv", "tensorboard"])
        # model.set_logger(new_logger)
    return model


def train_A2C_model(model, max_steps=80, model_path=os.path.join('RLTesting', 'logs', 'a2c.zip')):
    vec_env = model.get_env()
    vec_env.reset()
    vec_env.render()
    callback = TerminateOnDoneCallback(vec_env, verbose=1)
    model.learn(max_steps, callback=callback)
    action_state_list = vec_env.envs[0].get_state_action_pairs()
    model.save(model_path)
    vec_env.close()
    return action_state_list


def get_SAC_Model(env, model_path=os.path.join('RLTesting', 'logs', 'sac.zip')):
    if os.path.isfile(model_path):
        print("loading existing model")
        model = SAC.load(model_path, env=env)
    else:
        print("creating new model")
        model = SAC('MlpPolicy', env, verbose=1)
        new_logger = configure(folder="logs", format_strings=["stdout", "log", "csv", "tensorboard"])
        model.set_logger(new_logger)
    return model


def train_SAC_model(model, max_steps=80, model_path=os.path.join('RLTesting', 'logs', 'sac.zip')):
    vec_env = model.get_env()
    vec_env.reset()
    vec_env.render()
    callback = TerminateOnDoneCallback(vec_env, verbose=1)
    model.learn(max_steps, callback=callback)
    action_state_list = vec_env.envs[0].get_state_action_pairs()
    model.save(model_path)
    vec_env.close()
    return action_state_list


if __name__ == '__main__':
    # env = training_scripts.Env.EnvWrapper()
    # env.reset()
    # model = get_PPO_Model(env=env)
    # result = train_PPO_model(model=model)

    env1 = training_scripts.Env.EnvWrapper()
    model_a2c = get_A2C_Model(env=env1)
    result_a2c = train_PPO_model(model=model_a2c)

    # env2 = training_scripts.Env.EnvWrapper()
    # model_a2c = get_SAC_Model(env=env2)
    # result_a2c = train_SAC_model(model=model_a2c)
