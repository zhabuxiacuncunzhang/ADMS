'''
Descripttion: file content
version: 
Author: Xuesong_Zhang
Date: 2023-03-01 14:54:46
LastEditors: Xuesong_Zhang
LastEditTime: 2023-03-01 17:24:13
'''
import os
import sys
from PIL import Image
import pandas as pd
import numpy as np

"""
    裁剪并保存子图像左上角经纬度txt
"""


class HEADER:
    width = 0
    length = 0
    xfirst = 0.0
    yfirst = 0.0
    xstep = 0.0
    ystep = 0.0


def read_header(filename):
    if not os.path.isfile(filename):
        print(filename+" file not exit")

    header = HEADER()
    with open(filename) as f:
        for line in f:
            data = line.split()
            if data[0] == "WIDTH":
                header.width = int(data[1])
            if data[0] == "FILE_LENGTH":
                header.length = int(data[1])
            if data[0] == "X_FIRST":
                header.xfirst = float(data[1])
            if data[0] == "Y_FIRST":
                header.yfirst = float(data[1])
            if data[0] == "X_STEP":
                header.xstep = float(data[1])
            if data[0] == "Y_STEP":
                header.ystep = float(data[1])
    return header


def toCutPng(picPath, resultPath, x_first, y_first, dx, dy):
    if not os.path.exists(picPath):
        print("Can't find the file!")
        exit()
    if not os.path.isdir(resultPath):
        os.makedirs(resultPath)

    files = os.listdir(picPath)
    c0 = []
    c2 = []
    c3 = []
    c4 = []
    c5 = []
    for file in files:
        if os.path.splitext(file)[1] == '.png':
            a, b = os.path.splitext(file)  # 拆分影像图的文件名称
            this_dir = os.path.join(picPath + file)
            img = Image.open(this_dir)  # 按顺序打开某图片
            width, hight = img.size
            w = 800  # 宽度
            h = 800  # 高度
            _id = 1  # 裁剪结果保存文件名：0 - N 升序方式

            y = 0
            while (y + h <= hight):  # 控制高度,图像多余固定尺寸总和部分不要了
                x = 0
                while (x + w <= width):   # 控制宽度，图像多余固定尺寸总和部分不要了
                    new_img = img.crop((x, y, x + w, y + h))
                    new_img.save(resultPath + "/" + a + "_" + str(_id) + b)
                    aa = a + "_" + str(_id) + b
                    c0.append(aa)
                    _id += 1
                    xx = x_first+x*dx
                    c2.append(xx)
                    x += w
                    yy = y_first+y*dy
                    c3.append(yy)
                    c4.append(dx)
                    c5.append(dy)
                y = y + h
            c22 = np.round(c2, 8)
            c33 = np.round(c3, 8)
            c44 = np.round(c4, 10)
            c55 = np.round(c5, 10)
            tab = pd.DataFrame(
                {'pic_name': c0, 'sublon': c22, 'sublat': c33, 'xstep': c44, 'ystep': c55})
    tab.to_csv(resultPath + "/" + 'cut_tab.txt',
               sep=' ', index=False, header=False)


def main(argv):
    print("*****************************************")
    print("*       cut picture to subpic           *")
    print("*      Xuesong Zhang & Kelu He          *")
    print("*             2023.03.01                *")
    print("*****************************************")
    if (len(argv) < 3 or len(argv) > 3):
        print("usage:")
        print("    cutPic.py <header> <pic_path> <result_path>")
        print("        header       header file with path")
        print("        pic_path     *.png picture files path")
        print("        result_path  result path")
    else:
        header = read_header(argv[0])
        path = argv[1]
        result_path = argv[2]
        toCutPng(path, result_path, header.xfirst,
                 header.yfirst, header.xstep, header.ystep)


if __name__ == '__main__':
    main(sys.argv[1:])
