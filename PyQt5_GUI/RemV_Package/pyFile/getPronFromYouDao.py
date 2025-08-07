import os
# import subprocess
import urllib.request
import threading

from playsound import playsound

"""
@copyright   Copyright 2020 RemV
@license     GPL-3.0 (http://www.gnu.org/licenses/gpl-3.0.html)
@author      Lingao Xiao 肖凌奥 <920338028@qq.com>
@version     version 1.1
@link        https://github.com/ArmandXiao/RemV.git
"""

# 添加播放状态标志
is_playing = False
play_lock = threading.Lock()

def downloadMP3FromYouDao(word, type_):
    word = word.replace(" ", "%20")
    url = "http://dict.youdao.com/dictvoice?type=%d&audio=%s" % (type_, word)
    current_file_path = os.path.dirname(os.path.abspath(__file__))
    path = current_file_path + r"\lib\res\pron"
    fileName = word + "_" + str(type_) + ".mp3"

    filePath = os.path.join(path, fileName)

    if not os.path.exists(filePath):
        try:
            urllib.request.urlretrieve(url, filePath)
        except:
            sayTipSound()
            return ""
    else:
        print("mp3文件已存在")

    return filePath


def playSound(word, type_):
    global is_playing
    # 检查是否正在播放
    with play_lock:
        if is_playing:
            return  # 如果正在播放，则直接返回，防止重复播放

        path = downloadMP3FromYouDao(word, type_)
        if path != "":
            is_playing = True
        else:
            if type_ == 0:
                type_ = 1
            else:
                type_ = 0
            path = downloadMP3FromYouDao(word, type_)
            if path == "":
                is_playing = True
            else:
                return  # 下载失败则直接返回

    try:
        playsound(path)
    except Exception as e:
        print(f"播放音频时出错: {e}")
    finally:
        # 播放完成后重置标志
        with play_lock:
            is_playing = False
        # 删除临时文件
        # try:
        #     if os.path.exists(path):
        #         os.remove(path)
        # except Exception as e:
        #     print(f"删除临时音频文件时出错: {e}")


def sayTipSound():
    playsound(r"lib\res\pron\Please%20check%20your%20internet%20connection_0.mp3")
