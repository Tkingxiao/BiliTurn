import os  
import json  
import subprocess  
import pathlib  
import re  
import sys  # 添加这一行

# 执行 delete.py
def run_delete_script():
    if getattr(sys, 'frozen', False):
        # 获取临时路径
        base_path = sys._MEIPASS
        delete_script_path = os.path.join(base_path, 'delete.py')
    else:
        delete_script_path = os.path.join(os.getcwd(), 'delete.py')

    subprocess.run(['python', delete_script_path])

# 获取当前工作目录  
current_dir = pathlib.Path(os.getcwd())  

# 设置输入和输出目录  
input_dir = current_dir / 'input'  
output_dir = current_dir / 'output'  

# 确保输出目录存在  
output_dir.mkdir(exist_ok=True)  

def sanitize_filename(title):  
    # 替换无效字符  
    sanitized_title = re.sub(r'[<>:"/\\|?*]', '', title)  
    return sanitized_title.strip()  

def get_output_filename(output_dir, base_name):  
    """  
    生成一个唯一的输出文件名。  
    """  
    counter = 1  
    filename = base_name  
    while (output_dir / filename).exists():  
        filename = f"P{counter}_{base_name}"  
        counter += 1  
    return filename  

def merge_videos_in_folder(folder_path):  
    # 读取 videoInfo.json 文件  
    video_info_path = folder_path / 'videoInfo.json'  
    if not video_info_path.exists():  
        print(f"videoInfo.json not found in {folder_path}")  
        return  

    with open(video_info_path, 'r', encoding='utf-8') as f:  
        video_info = json.load(f)  
        group_title = video_info.get('groupTitle', '')  
        title = video_info.get('title', '')  

    # 清理文件名  
    group_title = sanitize_filename(group_title)  
    title = sanitize_filename(title)  

    # 如果 groupTitle 和 title 相同，则只使用 title  
    if group_title == title:  
        base_output_filename = f"{title}.mp4"  
    else:  
        base_output_filename = f"{group_title}-{title}.mp4"  

    output_filename = get_output_filename(output_dir, base_output_filename)  
    output_path = output_dir / output_filename  

    # 获取文件夹内的所有 .m4s 文件  
    m4s_files = sorted([f for f in os.listdir(folder_path) if f.endswith('.m4s')])  

    # 如果找到了两个 .m4s 文件，进行合并  
    if len(m4s_files) == 2:  
        audio_path = os.path.join(folder_path, m4s_files[0])  # 假设第一个是音频  
        video_path = os.path.join(folder_path, m4s_files[1])  # 假设第二个是视频  
        merge_video(audio_path, video_path, str(output_path))  

        # 复制任意一个 .m4s 文件的元数据到输出文件  
        copy_file_metadata(os.path.join(folder_path, m4s_files[0]), str(output_path))  

        print(f'Merged and copied metadata of files in {folder_path} into {output_path}')  
    else:  
        print(f'Expected two .m4s files in {folder_path}, but found {len(m4s_files)}.')  

def merge_video(audio_path, video_path, output_path):  
    # 获取 ffmpeg.exe 的路径
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
        ffmpeg_path = os.path.join(base_path, 'ffmpeg.exe')
    else:
        ffmpeg_path = os.path.join(os.getcwd(), 'ffmpeg.exe')

    command = [  
        ffmpeg_path,  # 使用获取的 ffmpeg.exe 路径  
        '-i', audio_path,  
        '-i', video_path,  
        '-c:v', 'copy',  # 使用视频流编解码器复制  
        '-c:a', 'copy',  # 使用音频流编解码器复制  
        '-y',  # 覆盖输出文件而不提示  
        output_path  
    ]  
    try:  
        subprocess.run(command, check=True)  
    except subprocess.CalledProcessError as e:  
        print(f"Error occurred while merging videos: {e}")  

def copy_file_metadata(src_path, dst_path):  
    # 获取源文件的元数据  
    src_stat = os.stat(src_path)  
    # 复制元数据到目标文件（特别是最后修改时间和访问时间）  
    os.utime(dst_path, (src_stat.st_atime, src_stat.st_mtime))  

if __name__ == "__main__":  
    run_delete_script()  # 运行 delete.py
    # 遍历 input 目录中的所有数字命名的子文件夹  
    for item in os.listdir(input_dir):  
        folder_path = input_dir / item  
        if item.isdigit() and os.path.isdir(folder_path):  
            merge_videos_in_folder(folder_path)
