import os
import json
import subprocess
import pathlib
import shutil
import re
import sys

# 获取当前工作目录
current_dir = pathlib.Path(os.getcwd())

# 设置输入和输出目录
input_folder_path = current_dir / 'input'
output_dir = current_dir / 'output'

# 动态设置 ffmpeg_exe_path，以确保在打包后也能正确找到 ffmpeg.exe
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    # 如果程序已经被打包，使用临时目录
    ffmpeg_exe_path = pathlib.Path(sys._MEIPASS) / 'ffmpeg.exe'
else:
    # 如果程序未被打包，使用当前目录
    ffmpeg_exe_path = current_dir / 'ffmpeg.exe'

# 确保输出目录存在
output_dir.mkdir(exist_ok=True)

def merge_video(audio_path, video_path, temp_output_path, ffmpeg_exe_path):
    command = [
        str(ffmpeg_exe_path),
        '-i', audio_path,
        '-i', video_path,
        '-c', 'copy',
        '-y',
        str(temp_output_path)  # 确保是字符串
    ]
    subprocess.run(command, check=True)

def sanitize_filename(title):
    # 替换无效字符
    sanitized_title = re.sub(r'[<>:"/\\|?*]', '', title)
    return sanitized_title.strip()

def copy_file_metadata(src_path, dst_path):
    # 获取源文件的元数据
    src_stat = os.stat(src_path)
    # 复制元数据到目标文件
    os.utime(dst_path, (src_stat.st_atime, src_stat.st_mtime))

def process_files(input_folder_path, output_dir):
    seen_titles = set()

    for root, dirs, files in os.walk(input_folder_path):
        for dir in dirs:
            if dir.startswith('c_'):
                dir_path = os.path.join(root, dir)
                entry_json_path = os.path.join(dir_path, 'entry.json')
                if os.path.exists(entry_json_path):
                    with open(entry_json_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        part = data.get('page_data', {}).get('part', '')  # 从page_data中提取part
                        if part:
                            sanitized_title = sanitize_filename(part)
                            temp_output_path = os.path.join(dir_path, f"{sanitized_title}.mp4")  # 将sanitized_title赋值给temp.mp4
                            
                            # 查找包含音频和视频文件的子文件夹
                            audio_path = None
                            video_path = None
                            for sub_dir in os.listdir(dir_path):
                                sub_dir_path = os.path.join(dir_path, sub_dir)
                                if os.path.isdir(sub_dir_path):
                                    if audio_path is None and os.path.exists(os.path.join(sub_dir_path, 'audio.m4s')):
                                        audio_path = os.path.join(sub_dir_path, 'audio.m4s')
                                    if video_path is None and os.path.exists(os.path.join(sub_dir_path, 'video.m4s')):
                                        video_path = os.path.join(sub_dir_path, 'video.m4s')
                            
                            if audio_path and video_path:
                                merge_video(audio_path, video_path, temp_output_path, str(ffmpeg_exe_path))
                                final_output_path = output_dir / f"{sanitized_title}.mp4"
                                shutil.move(temp_output_path, str(final_output_path))
                                copy_file_metadata(video_path, str(final_output_path))
                            else:
                                print(f'Audio or video file not found in {dir_path}')

process_files(input_folder_path, output_dir)
