import os
import random
from itertools import combinations
import shutil


bug_group = [
    {
        'relative_path': "stable_baselines3",
        'lineno': -1, # no use
        'original_lines': [],
        'injected_lines': [],
        'realife_bug': False,
        'description': "Anything about this bug"
    }, # 0th bug
    {},
]



# If there's no confliction return True, otherwise return False
def check_injection_validation(bug_id_ist):
    
    # for temp_line in temp_bug[original_lines]:
        # if temp_line not in relative_file_data:
                
    return True



def inject_bugs(config):
    if config['specific_bug_flag']:
        bug_id_list = config['specified_bug_id']
    else:
        print('???????') # need to randomly generate bug versions
    
    if not check_injection_validation(bug_id_list):
        return "bug version invalid!!"
    
    for bug_id in bug_id_list:
        temp_bug = bug_group[bug_id]
        
        relative_file = open(temp_bug['relative_path'])
        relative_file_data = relative_file.read()
        
        for bug_line_index in range(len(temp_bug['original_lines'])):
            relative_file_data.replace(temp_bug['original_lines'][bug_line_index], temp_bug['injected_lines'][bug_line_index])

        with open(temp_bug['relative_path'], 'w', encoding='utf-8') as file:
            file.writelines(relative_file_data)
            
            
def recover_project(config):
    # 设置主文件夹和archive文件夹的路径
    main_folder = config.root_dir
    archive_folder = os.path.join(main_folder, 'archived_code')

    # 自动获取archive文件夹下的所有子文件夹
    subfolders = [f for f in os.listdir(archive_folder) if os.path.isdir(os.path.join(archive_folder, f))]

    # 遍历每个子文件夹
    for subfolder in subfolders:
        archive_subfolder_path = os.path.join(archive_folder, subfolder)
        main_subfolder_path = os.path.join(main_folder, subfolder)
    
        # 确保目标子文件夹存在
        os.makedirs(main_subfolder_path, exist_ok=True)
    
        # 遍历archive中的每个文件
        for filename in os.listdir(archive_subfolder_path):
            # 源文件路径
            file_source = os.path.join(archive_subfolder_path, filename)
        
            # 目标文件路径
            file_destination = os.path.join(main_subfolder_path, filename)
        
            # 复制文件
            shutil.copy(file_source, file_destination)
    return