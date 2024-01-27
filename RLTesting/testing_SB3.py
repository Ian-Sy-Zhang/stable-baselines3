import bug_lib as BL
import subprocess
import os
from datetime import date
import re
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.stats import linregress

import sys

sys.path.insert(0, './training_scripts/')
import training_scripts

import training_scripts.DQN_step_by_step as DQNS
from config_parser import parserConfig

import gymnasium as gym
from stable_baselines3 import DQN
from stable_baselines3.common.vec_env import DummyVecEnv
from training_scripts.Env import EnvWrapper
from stable_baselines3.common.logger import configure


def get_Frozen_lake_Env(rewarded_actions={0: 2, 1: 2, 2: 1, 6: 1, 10: 1, 14: 2}):
    # 创建一个游戏环境，例如Frozen-lake
    env = EnvWrapper()

    env.set_rewarded_actions(rewarded_actions)
    initial_state = env.reset()
    env.set_current_state(initial_state[0])
    return env


def get_DQN_Model(env, model_path=os.path.join('RLTesting', 'logs', 'dqn.zip')):
    if os.path.isfile(model_path):
        print("loading existing model")
        model = DQN.load(model_path, env=env)
    else:
        print("creating new model")
        model = DQN("MlpPolicy", env, verbose=1, batch_size=1)
        new_logger = configure(folder="logs", format_strings=["stdout", "log", "csv", "tensorboard"])
        model.set_logger(new_logger)
    return model


def train_model(model, max_steps=100, model_path=os.path.join('RLTesting', 'logs', 'dqn.zip')):
    vec_env = model.get_env()
    obs = vec_env.reset()
    vec_env.render(mode='human')

    action_state_list = []

    for step in range(max_steps):
        # 选择一个动作
        action, _states = model.predict(obs, deterministic=True)

        # 环境执行动作
        new_obs, reward, done, info = vec_env.step(action)

        action_state_list.append(str(obs) + ',' + str(action) + ',' + str(reward))
        print("state, action:" + str(obs) + str(action))

        # 存储新的转换到回放缓冲区
        model.replay_buffer.add(obs, new_obs, action, reward, done, info)

        # 检查回放缓冲区是否有足够的数据来进行学习
        if model.replay_buffer.size() > model.batch_size:
            # 执行一步学习
            model.train(gradient_steps=1)

        # 将新的观察结果设置为下一步的初始状态
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


def round_loop(config):
    BL.recover_project(config)
    BL.inject_bugs(config)

    # pip reinstall SB3 repository
    os.chdir("..")
    # os.system('ls')
    os.system('pip install -e .[docs,tests,extra]')

    for round in range(config['rounds']):
        print("round: " + str(round) + "----")

        log_dir = os.path.join(config['root_dir'], 'RLTesting', 'logs')
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        log_name = 'time_' + str(date.today()) + str(config['specified_bug_id']) + 'round_' + str(round)
        log_path = os.path.join(log_dir, log_name)
        with open(log_path, 'a') as log_file:
            log_file.write(str(config))
            log_file.write("\n-------------\n")

        # TODO: 每个round都需要重新随机生成env的rewarded_actions
        rewarded_actions = {0: 2, 1: 2, 2: 1, 6: 1, 10: 1, 14: 2}
        env = get_Frozen_lake_Env(rewarded_actions=rewarded_actions)
        with open(log_path, 'a') as log_file:
            log_file.write('rewarded_actions' + str(rewarded_actions))
            log_file.write("\n-------------\n")

        model_path = os.path.join('RLTesting', 'logs', 'dqn.zip')

        model = get_DQN_Model(env=env, model_path=model_path)

        for epoch in range(config['epoches']):
            actions_in_epoch = train_model(model, model_path=model_path)

            # print(actions_in_epoch)

            with open(log_path, 'a') as log_file:
                log_file.write('epoch: ' + str(epoch) + '\n')
                log_file.write(str(actions_in_epoch))
                log_file.write("\n-------------\n")

        os.remove(model_path)


def main(bug_version_list):
    config = parserConfig()

    for bug_version in bug_version_list:
        config['specified_bug_id'] = bug_version
        print(bug_version, config['specified_bug_id'])
        round_loop(config)


# initialize bug_version_list
bug_version_list = [
    # [0],
    # [1],
    # # ...,
    # [1,2,3]
    # [],
    [],
]

main(bug_version_list)
