#!/usr/bin/env python
# -*- coding: utf-8 -*-
try:
    import cStringIO as StringIO
except ImportError:
    import StringIO

from web import ctx

from PIL import Image,ImageDraw


def process_image(image):
    """
    处理验证码,使其只剩下红色字体
    """
    input_file=StringIO.StringIO(image)
    im = Image.open(input_file)
    draw = ImageDraw.Draw(im)
    length = im.size[0]
    height = im.size[1]
    for i in range(length):
        for j in range(height):
            c = im.getpixel((i,j))
            if c < 220:
                draw.point((i,j),255)
    region = im.crop((24,0,92,30))   # 裁剪图片(x1, y1, x2, y2)
    return region

def process_image_string(image):
    """
    传入图片的字符串, 返回处理后图片的字符串
    """

    #im = process_image(image)
    input_file=StringIO.StringIO(image)
    im = Image.open(input_file)

    output_file=StringIO.StringIO()
    im.save(output_file, format='gif')

    content = output_file.getvalue()
    output_file.close()

    return content
