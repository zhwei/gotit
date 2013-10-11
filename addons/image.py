#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PIL import Image,ImageDraw

import cStringIO

def process_image(pwd):
    """
    处理验证码,使其只剩下红色字体
    """
    im = Image.open(pwd)
    draw = ImageDraw.Draw(im)
    length = im.size[0]
    height = im.size[1]
    for i in range(length):
        for j in range(height):
            c = im.getpixel((i,j))
            if c < 220:
                draw.point((i,j),255)
    #im.save(pwd) # in version 2.0
    return im

def process_image_string(image):
    """
    传入图片的字符串, 返回处理后图片的字符串
    """
    input_file=cStringIO.StringIO(image)
    output_file=cStringIO.StringIO()

    im = process_image(input_file)
    im.save(output_file, format='gif')

    content = output_file.getvalue()
    output_file.close()

    return content
