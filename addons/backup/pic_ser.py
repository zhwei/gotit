#!/usr/bin/env python
# -*- coding: utf-8 -*-

#import Image
import pickle

im = file('a.gif','r')

image = pickle.load(im)

print len(image)
