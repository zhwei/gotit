#!/usr/bin/env python
# -*- coding: utf-8 -*-

from code import app

def dev_server():
    app.run()

if __name__ == "__main__":
    from django.utils import autoreload
    autoreload.main(dev_server)
