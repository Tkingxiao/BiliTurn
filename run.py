import os
import json
import subprocess
import pathlib
import sys

# 获取脚本所在的目录
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    script_dir = pathlib.Path(sys._MEIPASS)
else:
    script_dir = pathlib.Path(__file__).parent

# 设置输入和输出目录为与脚本同级的目录
input_folder_path = script_dir / 'input'
output_dir = script_dir.parent / 'output'  # 将输出目录设置为与run.exe同级的目录
ffmpeg_exe_path = script_dir / 'ffmpeg.exe'

# 确保输出目录存在
output_dir.mkdir(exist_ok=True)

def merge_video(audio_path, video_path, output_path, ffmpeg_exe_path):
    command = [
        str(ffmpeg_exe_path),
        '-i', audio_path,
        '-i', video_path,
        '-c', 'copy',
        '-y',
        output_path
    ]
    subprocess.run(command, check=True)

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
                            base_output_video_name = title + '.mp4'
                            output_video_name = base_output_video_name
                            prefix = 1
                            while output_video_name in seen_titles or (output_dir / output_video_name).exists():
                                prefix += 1
                                output_video_name = f"P{prefix} {base_output_video_name}"

                            seen_titles.add(output_video_name)
                            output_video_path = output_dir / output_video_name

                            audio_path = os.path.join(dir_path, '16', 'audio.m4s')
                            video_path = os.path.join(dir_path, '16', 'video.m4s')

                            if os.path.exists(audio_path) and os.path.exists(video_path):
                                merge_video(audio_path, video_path, str(output_video_path), str(ffmpeg_exe_path))
                                print(f'Merged {audio_path} and {video_path} into {output_video_path}')
                            else:
                                print(f'Audio or video file not found in {dir_path}')

process_files(input_folder_path)
