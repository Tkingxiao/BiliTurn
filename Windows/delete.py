import os
import pathlib

def remove_leading_thirties(file_path):
    """
    删除文件开头直到第一个0000之前的所有30。
    """
    with open(file_path, 'rb') as f:
        data = f.read()

    # 查找第一个0000的位置
    zero_index = data.find(b'\x00\x00')
    if zero_index == -1:
        print(f"No double zero found in {file_path}.")
        return False

    # 计算需要删除的30的数量
    thirty_count = 0
    for i in range(zero_index):
        if data[i] == ord(b'\x30'):
            thirty_count += 1
        else:
            break

    # 删除前thirty_count个30
    new_data = data[thirty_count:]
    with open(file_path, 'wb') as f:
        f.write(new_data)
    return True

def remove_trailing_sequence(file_path, sequence):
    """
    从文件的最后一行开始往前删除，直到没有更多的特定序列。
    """
    with open(file_path, 'rb') as f:
        data = f.read()

    # 查找并修剪重复序列
    sequence_len = len(sequence)
    end = len(data) - sequence_len
    while end >= 0:
        # 检查当前位置是否为我们要找的序列
        if data[end:end+sequence_len] == sequence:
            # 删除找到的序列
            data = data[:end] + data[end+sequence_len:]
            end -= sequence_len  # 更新结束位置，继续往前查找
        else:
            break  # 如果当前位置不是我们要查找的序列，停止处理

    # 重写文件
    with open(file_path, 'wb') as f:
        f.write(data)

def process_file(file_path, sequence):
    """
    处理单个文件，删除开头的30和末尾的重复序列。
    """
    if remove_leading_thirties(file_path):
        remove_trailing_sequence(file_path, sequence)
    else:
        print(f"Skipping {file_path} due to no double zero found.")

def process_directory(directory_path, sequence):
    """
    处理目录中的所有.m4s文件。
    """
    for file_name in os.listdir(directory_path):
        if file_name.endswith('.m4s'):
            file_path = os.path.join(directory_path, file_name)
            process_file(file_path, sequence)

# 设置输入目录
input_dir = pathlib.Path('input')

# 特定的重复序列
sequence = b'\x21\x11\x45\x00\x14\x50\x01\x47'

# 遍历input目录中的所有数字文件夹
for dir_name in os.listdir(input_dir):
    dir_path = input_dir / dir_name
    if dir_name.isdigit() and os.path.isdir(dir_path):
        process_directory(dir_path, sequence)