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
    # path = downloadMP3FromYouDao(word, type_)
    # if path != "":
        # playsound(path)
        # del
        #cmd = r"del %s" % path
        #subprocess.call(cmd, shell=True)
    global is_playing

    # 检查是否正在播放
    with play_lock:
        global is_playing
        if is_playing:
            return  # 如果正在播放，则直接返回，防止重复播放

        path = downloadMP3FromYouDao(word, type_)
        if path != "":
            is_playing = True

    try:
        if path != "":
            playsound(path)
    finally:
        # 播放完成后重置标志
        with play_lock:
            global is_playing
            is_playing = False


def sayTipSound():
    playsound(r"lib\res\pron\Please%20check%20your%20internet%20connection_0.mp3")
