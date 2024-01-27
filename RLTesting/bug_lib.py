import os
import random
from itertools import combinations
import shutil


bug_group = [
    {
        'relative_path': "/stable_baselines3/dqn/dqn.py",
        'lineno': -1, # no use
        'original_lines': ['tau: float = 1.0,'],
        'injected_lines': ['tau: float = 2.0,  # should be within 0 and 1, buggy'],
        'realife_bug': False,
        'description': "Anything about this bug"
    }, # 0th bug
    {
        'relative_path': "/stable_baselines3/dqn/dqn.py",
        'lineno': -1, # no use
        'original_lines': ['th.nn.utils.clip_grad_norm_(self.policy.parameters(), self.max_grad_norm)'],
        'injected_lines': ['# th.nn.utils.clip_grad_norm_(self.policy.parameters(), self.max_grad_norm)  # buggy'],
        'realife_bug': False,
        'description': "Anything about this bug"
    }, # 1st bug
    {
        'relative_path': "/stable_baselines3/dqn/dqn.py",
        'lineno': -1,  # no use
        'original_lines': ['polyak_update(self.batch_norm_stats, self.batch_norm_stats_target, 1.0)'],
        'injected_lines': ['polyak_update(self.batch_norm_stats, self.batch_norm_stats_target, self.tau)  # 错误的方法'],
        'realife_bug': False,
        'description': "Anything about this bug"
    },  # 2nd bug
    {
        'relative_path': "/stable_baselines3/dqn/dqn.py",
        'lineno': -1,  # no use
        'original_lines': ['if self._n_calls % max(self.target_update_interval // self.n_envs, 1) == 0:'],
        'injected_lines': ['if self._n_calls % max(0 // self.n_envs, 1) == 0:'],
        'realife_bug': False,
        'description': "Anything about this bug"
    },  # 3rd bug
    {
        'relative_path': "/stable_baselines3/dqn/dqn.py",
        'lineno': -1,  # no use
        'original_lines': ['self.exploration_initial_eps,', 'self.exploration_final_eps, #'],
        'injected_lines': ['self.exploration_final_eps,', 'self.exploration_initial_eps,'],
        'realife_bug': False,
        'description': "Anything about this bug"
    },  # 4th bug
]



# If there's no confliction return True, otherwise return False
def check_injection_validation(bug_id_ist):
    
    # for temp_line in temp_bug[original_lines]:
        # if temp_line not in relative_file_data:
                
    return True



def inject_bugs(config):
    # if config['specific_bug_flag']:
    bug_id_list = config['specified_bug_id']
    # else:
        # print('???????') # need to randomly generate bug versions
    
    if not check_injection_validation(bug_id_list):
        return "bug version invalid!!"
    
    for bug_id in bug_id_list:
        temp_bug = bug_group[bug_id]

        temp_bug_path = config['root_dir'] + temp_bug['relative_path']
        
        relative_file = open(temp_bug_path)
        relative_file_data = relative_file.read()
        print(relative_file_data)

        for bug_line_index in range(len(temp_bug['original_lines'])):
            relative_file_data.replace(temp_bug['original_lines'][bug_line_index], temp_bug['injected_lines'][bug_line_index])

        relative_file.writelines(relative_file_data)
        relative_file.close()
            
            
# def recover_project(config):
#     # 设置主文件夹和archive文件夹的路径
#     main_folder = config['root_dir']
#     archive_folder = os.path.join(main_folder, 'archived_code')

#     # 自动获取archive文件夹下的所有子文件夹
#     subfolders = [f for f in os.listdir(archive_folder) if os.path.isdir(os.path.join(archive_folder, f))]

#     # 遍历每个子文件夹
#     for subfolder in subfolders:
#         archive_subfolder_path = os.path.join(archive_folder, subfolder)
#         main_subfolder_path = os.path.join(main_folder, subfolder)
    
#         # 确保目标子文件夹存在
#         os.makedirs(main_subfolder_path, exist_ok=True)
    
#         # 遍历archive中的每个文件
#         for filename in os.listdir(archive_subfolder_path):
#             # 源文件路径
#             file_source = os.path.join(archive_subfolder_path, filename)
        
#             # 目标文件路径
#             file_destination = os.path.join(main_subfolder_path, filename)
        
#             # 复制文件
#             shutil.copy(file_source, file_destination)
#     return
        
def recover_project(config):
    main_folder = config['root_dir']
    archive_folder = os.path.join(main_folder, 'archived_code')

    # 确保存档文件夹存在
    if not os.path.exists(archive_folder):
        print(f"Archive folder not found: {archive_folder}")
        return

    # 获取archive文件夹下的所有子文件夹
    subfolders = [f for f in os.listdir(archive_folder) if os.path.isdir(os.path.join(archive_folder, f))]

    for subfolder in subfolders:
        archive_subfolder_path = os.path.join(archive_folder, subfolder)
        main_subfolder_path = os.path.join(main_folder, subfolder)

        # 如果目标文件夹存在，则先删除（shutil.copytree要求目标文件夹不存在）
        if os.path.exists(main_subfolder_path):
            shutil.rmtree(main_subfolder_path)

        # 复制整个目录树
        shutil.copytree(archive_subfolder_path, main_subfolder_path)