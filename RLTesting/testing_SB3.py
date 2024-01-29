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

import random


def get_Frozen_lake_Env(rewarded_actions={0: 2, 1: 2, 2: 1, 6: 1, 10: 1, 14: 2}):
    # 创建一个游戏环境，例如Frozen-lake
    env = EnvWrapper()

    env.set_rewarded_actions(rewarded_actions)
    initial_state = env.reset()
    env.set_current_state(initial_state[0])
    return env


def get_random_station_action_rewarder(env):
    state_action_dict = {}
    lake_size = int(env.observation_space.n ** 0.5)  # Assuming the lake is a square
    goal_state = env.observation_space.n - 1  # Assuming the goal state is the last one

    # 遍历所有状态
    for state in range(env.observation_space.n):
        safe_actions = []

        # 检查当前状态下的所有动作
        for action in range(env.action_space.n):
            # 获得执行动作后的潜在结果列表
            transitions = env.P[state][action]

            # 检查每个潜在结果，确保它不会导致掉入冰窟（H）或走出边界
            for transition in transitions:
                prob, next_state, reward, done = transition
                if prob == 1.0:
                    # 如果下一个状态是终点，则这个动作是安全的
                    if next_state == goal_state:
                        safe_actions.append(action)
                        break
                    row, col = divmod(next_state, lake_size)
                    # 检查是否会走出边界
                    if action == 0 and col == 0:  # 左动作，当前在最左列
                        continue
                    if action == 1 and row == (lake_size - 1):  # 下动作，当前在最下行
                        continue
                    if action == 2 and col == (lake_size - 1):  # 右动作，当前在最右列
                        continue
                    if action == 3 and row == 0:  # 上动作，当前在最上行
                        continue
                    # 检查下一个状态是否是洞（H）
                    if env.desc.reshape(-1)[next_state] != b'H':
                        safe_actions.append(action)
                        break  # 适用于确定性环境，无需检查其他transition

        # 如果有安全的动作，随机选择一个
        if safe_actions:
            action = random.choice(safe_actions)
            state_action_dict[state] = action

    # state15表示已经到达终点，不需要采取其他任何动作
    if 15 in state_action_dict:
        del state_action_dict[15]

    # 随机丢弃生成的script中的一些内容
    keys = list(state_action_dict.keys())
    random.shuffle(keys)  # 打乱键的顺序
    keys_to_remove = keys[:len(keys)//4]  # 准备取走四分之一的键

    for key in keys_to_remove:
        del state_action_dict[key]  # 从字典中移除选中的键

    return state_action_dict


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

        # 每个round都需要重新随机生成env的rewarded_actions
        # rewarded_actions = {0: 2, 1: 2, 2: 1, 6: 1, 10: 1, 14: 2}
        env = get_Frozen_lake_Env()
        rewarded_actions = get_random_station_action_rewarder(env)
        env.set_rewarded_actions(rewarded_actions)
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
    # [0],
    # [1],
    # [2],
    # [3],
    # [4],
]

main(bug_version_list)
