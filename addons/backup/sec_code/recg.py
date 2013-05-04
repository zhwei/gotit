#!/usr/bin/env python
# -*- coding: utf-8 -*-
# coding:utf-8
from PIL import Image, ImageDraw
import Image
from PIL import Image, ImageDraw
from pytesser import image_to_string
import urllib2
import os
import random


#二值判断,如果确认是噪声,用改点的上面一个点的灰度进行替换
#该函数也可以改成RGB判断的,具体看需求如何
def getPixel(image, x, y, G, N):
    L = image.getpixel((x, y))
    if L > G:
        L = True
    else:
        L = False

    nearDots = 0
    if L == (image.getpixel((x - 1, y - 1)) > G):
        nearDots += 1
    if L == (image.getpixel((x - 1, y)) > G):
        nearDots += 1
    if L == (image.getpixel((x - 1, y + 1)) > G):
        nearDots += 1
    if L == (image.getpixel((x, y - 1)) > G):
        nearDots += 1
    if L == (image.getpixel((x, y + 1)) > G):
        nearDots += 1
    if L == (image.getpixel((x + 1, y - 1)) > G):
        nearDots += 1
    if L == (image.getpixel((x + 1, y)) > G):
        nearDots += 1
    if L == (image.getpixel((x + 1, y + 1)) > G):
        nearDots += 1

    if nearDots < N:
        return image.getpixel((x, y - 1))
    else:
        return None

# 降噪
# 根据一个点A的RGB值，与周围的8个点的RBG值比较，设定一个值N（0 <N <8），当A的RGB值与周围8个点的RGB相等数小于N时，此点为噪点
# G: Integer 图像二值化阀值
# N: Integer 降噪率 0 <N <8
# Z: Integer 降噪次数
# 输出
#  0：降噪成功
#  1：降噪失败


def clearNoise(image, G, N, Z):
    draw = ImageDraw.Draw(image)

    for i in xrange(0, Z):
        for x in xrange(1, image.size[0] - 1):
            for y in xrange(1, image.size[1] - 1):
                color = getPixel(image, x, y, G, N)
                if color != None:
                    draw.point((x, y), color)

#测试代码


def rec(image):
    #打开图片
    #image = Image.open(name)
    #将图片转换成灰度图片
    image = image.convert("L")
    #去噪,G = 50,N = 4,Z = 4
    clearNoise(image, 50, 2, 11)
    #保存图片
    #image.save("r" + name)
    return image


# 二值化
threshold = 140
table = []
for i in range(256):
    if i < threshold:
        table.append(0)
    else:
        table.append(1)


def verify(name):
    #打开图片
    im = Image.open(name)
    #转化到亮度
    imgry = im.convert('L')
    #imgry.save('a' + name)
    #二值化
    out = imgry.point(table, '1')
    #out.save('b' + name)

    out = rec(out)
    #out.save('c' + name)
    #识别
    text = image_to_string(out)
    #识别对吗
    text = text.strip()
    text = text.upper()
    #os.system('rm '+name)
    return text[0:4]

def url_recg(url):
    name = str(random.randint(0,1000)) + '.gif'
    print name
    html = urllib2.urlopen(url).read()
    open(name,'wb').write(html)
    return verify(name)
