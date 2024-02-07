import bug_lib as BL
import subprocess
import os

import sys

sys.path.insert(0, './training_scripts/')

from stable_baselines3 import DQN
from stable_baselines3.common.logger import configure

import random

def get_DQN_Model(env, model_path=os.path.join('RLTesting', 'logs', 'dqn.zip')):
    if os.path.isfile(model_path):
        print("loading existing model")
        model = DQN.load(model_path, env=env)
    else:
        print("creating new model")
        model = DQN("MlpPolicy",
                    env,
                    verbose=1,
                    batch_size=1,
                    exploration_fraction=0.1,  # 探索率将在训练的10%的时间内衰减
                    exploration_initial_eps=1.0,  # 初始探索率100%
                    exploration_final_eps=0.01)  # 最终探索率1%
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


def get_PPO_Model(env, model_path):
    return

def train_PPO_model(model, max_steps=80, model_path=os.path.join('RLTesting', 'logs', 'dqn.zip')):
    return


def get_A2C_Model(env, model_path):
    return


def train_A2C_model(model, max_steps=80, model_path=os.path.join('RLTesting', 'logs', 'dqn.zip')):
    return