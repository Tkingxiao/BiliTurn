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
        temp_output_path
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
                                merge_video(audio_path, video_path, temp_output_path, str(ffmpeg_exe_path))
                                final_output_path = output_dir / output_video_name
                                shutil.move(temp_output_path, str(final_output_path))
                                copy_file_metadata(video_path, str(final_output_path))
                            else:
                                print(f'Audio or video file not found in {dir_path}')

process_files(input_folder_path, output_dir)