import os
import json
import subprocess
import pathlib
import shutil
import re

# 获取当前工作目录
current_dir = pathlib.Path(os.getcwd())

# 设置输入和输出目录
input_folder_path = current_dir / 'input'  # 输入文件夹在同级目录下
output_dir = current_dir / 'output'          # 输出文件夹在同级目录下
ffmpeg_exe_path = current_dir / 'ffmpeg.exe'  # ffmpeg.exe也在同级目录下

# 确保输出目录存在
output_dir.mkdir(exist_ok=True)

def merge_video(audio_path, video_path, temp_output_path, ffmpeg_exe_path):
    command = [
        str(ffmpeg_exe_path),
        '-i', audio_path,
        '-i', video_path,
        '-c', 'copy',
        '-y',
        temp_output_path
    ]
    subprocess.run(command, check=True)

def sanitize_filename(title):
    # 替换无效字符
    sanitized_title = re.sub(r'[<>:"/\\|?*]', '', title)  # 移除无效字符
    return sanitized_title.strip()  # 去除首尾空格

def process_files(input_folder_path):
    seen_titles = set()

    for root, dirs, files in os.walk(input_folder_path):
        for dir in dirs:
            if dir.startswith('c_'):
                dir_path = os.path.join(root, dir)
                entry_json_path = os.path.join(dir_path, 'entry.json')
                if os.path.exists(entry_json_path):
                    with open(entry_json_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        title = data.get('title', '')
                        if title:
                            sanitized_title = sanitize_filename(title)
                            base_output_video_name = sanitized_title + '.mp4'
                            output_video_name = base_output_video_name
                            prefix = 1
                            while output_video_name in seen_titles or (output_dir / output_video_name).exists():
                                prefix += 1
                                output_video_name = f"P{prefix} {base_output_video_name}"

                            seen_titles.add(output_video_name)

                            temp_output_path = os.path.join(dir_path, 'temp.mp4')
                            audio_path = os.path.join(dir_path, '16', 'audio.m4s')
                            video_path = os.path.join(dir_path, '16', 'video.m4s')

                            if os.path.exists(audio_path) and os.path.exists(video_path):
                                # 生成 temp.mp4 文件
                                merge_video(audio_path, video_path, temp_output_path, str(ffmpeg_exe_path))
                                print(f'Merged {audio_path} and {video_path} into {temp_output_path}')

                                # 移动 temp.mp4 到 output 文件夹
                                temp_output_in_output_dir = output_dir / 'temp.mp4'
                                shutil.move(temp_output_path, temp_output_in_output_dir)
                                print(f'Moved {temp_output_path} to {temp_output_in_output_dir}')

                                # 重命名为提取的 title 加上 .mp4
                                final_output_path = output_dir / output_video_name
                                temp_output_in_output_dir.rename(final_output_path)
                                print(f'Renamed to {final_output_path}')
                            else:
                                print(f'Audio or video file not found in {dir_path}')

process_files(input_folder_path)
