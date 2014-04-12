#!/usr/bin/env python
# -*- coding: utf-8 -*-
# coding:utf-8

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFilter


from itertools import product
from pytesser import image_to_string


def process_image(name):
    #打开图片
    image = Image.open(name)
    image = image.convert("RGB")
    draw = ImageDraw.Draw(image)
    for x, y in product(range(image.size[0]), range(image.size[1])):
        color_tuple = image.getpixel((x, y))
        if color_tuple !=  (255, 0, 0):
            draw.point((x, y), (255, 255, 255)) # remove other color
        else:
            draw.point((x, y), (0, 0, 0)) # turn black
    image = image.filter(ImageFilter.DETAIL)
    image.save("zzzzz.png")
    return image


def verify(image):
    """ 识别中文验证码
    """

    im = process_image(image)

    text = image_to_string(im)

    return "%s%s"%(text[0], text[-1])
