#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PIL import Image,ImageDraw

def process_image(image):
    """
    处理验证码,使其只剩下红色字体
    """
    im = Image.open(image)
    draw = ImageDraw.Draw(im)
    length = im.size[0]
    height = im.size[1]
    for i in range(length):
        for j in range(height):
            c = im.getpixel((i,j))
            if c < 220:
                draw.point((i,j),255)
    im.show()
    im.save(image)
