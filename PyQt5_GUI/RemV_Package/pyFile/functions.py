import csv
import os
import re
import threading

import openpyxl
import re
import urllib.request as uR
import urllib.parse as uP
import json

import xlrd

import dataBase_Tools

"""
@copyright   Copyright 2020 RemV
@license     GPL-3.0 (http://www.gnu.org/licenses/gpl-3.0.html)
@author      Lingao Xiao 肖凌奥 <920338028@qq.com>
@version     version 1.1
@link        https://github.com/ArmandXiao/RemV.git
"""


def translator(content):
    """
    Translate words automatically
    :param content: 英文单词 type: str
    :return: 翻译 type: str
    """

    # 要把 _o 从url中删除 因为这是反爬机制
    url = "http://fanyi.youdao.com/translate?smartresult=dict&smartresult=rule"

    data = {
        'i': content,
        'from': 'AUTO',
        'to': 'AUTO',
        'smartresult': 'dict',
        'client': 'fanyideskweb',
        'salt': '15823838172021',
        'sign': '835107d66fdbf50ec298924d963a1321',
        'ts': '1582383817202',
        'bv': '901200199a98c590144a961dac532964',
        'doctype': 'json',
        'version': '2.1',
        'keyfrom': 'fanyi.web',
        'action': 'FY_BY_CLICKBUTTION',
    }

    data = uP.urlencode(data).encode('UTF-8')
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) " "Chrome/79.0.3945.130 Safari/537.36",
    }

    # 访问的时候加 上 header, 防止电脑知道你是爬虫
    req = uR.Request(url, data, header)

    response = uR.urlopen(req)

    html = response.read().decode('UTF-8')

    target = json.loads(html)
    return target["translateResult"][0][0]["tgt"]

    # print("翻译结果: %s\n下一次程序将在3秒后执行，输入 quit! 可退出程序" % (target["translateResult"][0][0]["tgt"]))


def excelParse_xlrd(path_, pattern=0):
    """
    xlrd read excels more efficiently than openpyxl, but xlrd cannot write excels
    @:parameter:path_: give a path
    @:parameter: pattern: 0 represents not creating a csv file, 1 represent creating a csv file.
    @:return: a list tha contains word and meanings, which ought to be easily converted to csv.
    """
    # 把path转成 raw String, 避免转义错误
    wb1 = xlrd.open_workbook(r"" + path_)

    # 暂时的 需要修改成 General 的
    sheet = wb1.sheet_by_index(0)

    numRow = sheet.nrows

    findNum = re.compile(r"[0-9]")

    myList = []

    global f, writer, wordList

    if pattern:
        wordList = []

    index = 0
    while index < numRow:
        word = str(sheet.row(index)[0].value).strip()
        pos = str(sheet.row(index)[1].value).strip()
        meaning = str(sheet.row(index)[2].value).strip()
        # sheet.row(rowNumber)[column].value -> cell value
        if len(findNum.findall(word)) > 0:
            index += 1
            continue

        if (sheet.row(index)[0].value is not None) and (re.sub(r"[ ,-?']", "a", word).encode("utf-8").isalpha()):
            # myList[index][0]是 单词
            # myList[index][1][0] 是 词性
            # myList[index][1][1] 是 意思
            myList.append((word, (pos, meaning)))
            if pattern:
                wordList.append(word)
        index += 1

    if pattern:
        newThread = threading.Thread(target=dataBase_Tools.writeCSV, args=(getFileName(path_), wordList))
        newThread.setDaemon(False)
        newThread.start()

    return myList


def parseCsv(path_):
    """
    Gives back a list through parsing csv, for parsing csv saves more time than parsing excels again
    Pattern: [word,pos,translation,phonetic,collins,tag,definition,exchange]
    :param path_: path of csv file
    :return: a list tha contains word and meanings.
    """

    list_ = []

    with open(path_) as f:
        read = csv.reader(f)
        for eachRow in read:
            # [word,pos,translation,phonetic,collins,tag,definition,exchange]
            list_.append((eachRow[0], (eachRow[1], eachRow[2], eachRow[3], eachRow[4], eachRow[5], eachRow[6], eachRow[7])))

    return list_


def excelParse(path_):
    """
    要给绝对路径 NOT relative path
    不知道为什么相对路径在 VsCode 可以打开 但是 PyCharm 不行  很奇怪
    """
    # 把path转成 raw String, 避免转义错误
    wb1 = openpyxl.load_workbook(r"" + path_)

    # 暂时的 需要修改成 General 的
    ws3 = wb1.active

    findNum = re.compile(r"[0-9]")

    myList = []

    # use try here because ErrorBook may have nothing in it
    try:
        for eachRow in ws3:
            # eachRow[0]是每行第一个cell，加上 .value 是cell里面的值
            # debug: None Obejct has no attribute: encode()
            # debug: int has no attribute: encode()
            if len(findNum.findall(str(eachRow[0].value))) > 0:
                continue

            # check whether the cell is an English word
            if (eachRow[0].value is not None) and (str(eachRow[0].value).strip().replace(" ", "a").encode("utf-8").isalpha()):
                # myList[index][0]是 单词
                # myList[index][1][0] 是 词性
                # myList[index][1][1] 是 意思
                myList.append((eachRow[0].value.strip(), (eachRow[1].value, eachRow[2].value)))
    except:
        pass

    return myList


def getFileName(path_):
    '''
    获取文件的名字，如果包含_remv 就删除
    :param path_: 文件路径
    :return: String 文件名字
    '''
    newPath = r"" + path_
    # 系统给的文件名字是 中的 是 /
    getName = re.compile(r"\\|[.]|/")
    excelname = getName.split(newPath)
    if "_remv" in excelname[len(excelname) - 2]:
        return excelname[len(excelname) - 2].split("_remv")[0]
    else:
        return excelname[len(excelname) - 2]


def getBooks(list_):
    '''
    :param list_: a list that contains file paths or a str (path)
    :return: A dictionary: key-> bookName, value: -> file path
    '''
    # 判读用户输入的是 一个path 还是一个list的path
    if type(list_) is list:
        dict1 = {}
        for item in list_:
            dict1.update({getFileName(item): item})
        return dict1

    if type(list_) is str:
        dict1 = {}
        dict1.update({getFileName(list_): list_})
        return dict1

    return None


def getBookNames(pathList):
    """
    :param pathList:
    :return: List of names
    """
    list_ = []
    for item in pathList:
        list_.append(getFileName(item))
    return list_


def divideIntoLessons(list_, num=20):
    """
    :param list_: a list that has been parsed already. Each element in the list should be a tuple. Each tuple represents a word.
    :param num: how many vocabularies that you want in one lesson. Default num is 20.
    :return: a list that contains other lists. Each element in this list is a list that contains at most (num) tuples.
    """
    lessonList = []
    # 地板除 整除
    lessons = len(list_) // num
    count = 0
    for i in range(lessons):
        # debug: += 千万不能写成 =
        # debug: += 把list分开了 因为太只能 所以把list里面每个值 加到 lessonList 里面了
        lessonList.append(list_[count : (count + num)])
        count += num
    lessonList.append(list_[count:])
    # print(lessonList)
    return lessonList


if __name__ == '__main__':
    pass
    # path = r"C:\Users\Armand\PycharmProjects\RemV\PyQt5_GUI\RemV_Package\单词库\出国研究生\新GRE官方词汇.xlsx"
    # start = time.time()
    # myList = excelParse_xlrd(path, 1)
    # tmp = str(time.time() - start)
    #
    # print("总花费时长:" + tmp)
