import stable_baselines3
# from configparser import ConfigParser
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

import training_scripts.DQN as DQN
import training_scripts.DQN_step_by_step as DQNS
from config_parser import parserConfig


def round_loop(config):
    for round in range(config['rounds']):
        print("round: " + str(round) + "----")
        BL.recover_project(config)
        BL.inject_bugs(config)

        # pip重新安装repository
        os.chdir("..")
        # os.system('ls')
        os.system('pip install -e .[docs,tests,extra]')

        # log_dir = config['root_dir'] + '/logs/'
        log_dir = os.path.join(config['root_dir'],  'RLTesting', 'logs')
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        log_name = 'time_' + str(date.today()) + str(config['specified_bug_id']) + 'round_' + str(round)
        log_path = os.path.join(log_dir, log_name)
        with open(log_path, 'a') as log_file:
            log_file.write(str(config))
            # print(str(config))
            log_file.write("\n-------------\n")

        for epoch in range(config['epoches']):
            # actions_in_epoch = DQN.training_sript()
            actions_in_epoch = DQNS.training_script()

            print(actions_in_epoch)

            with open(log_path, 'a') as log_file:
                log_file.write('epoch: ' + str(epoch) + '\n')
                log_file.write(str(actions_in_epoch))
                # print(str(config))
                log_file.write("\n-------------\n")

            # training_script = + '' # path of training script

            # run_python_and_capture_print(training_script, log_name)


# initialize bug_version_list
bug_version_list = [
    # [0],
    # [1],
    # # ...,
    # [1,2,3]
    # [],
    [],
]


def main(bug_version_list):
    config = parserConfig()

    for bug_version in bug_version_list:
        config['specified_bug_id'] = bug_version
        print(bug_version, config['specified_bug_id'])
        round_loop(config)


main(bug_version_list)