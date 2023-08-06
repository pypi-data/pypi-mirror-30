#!/usr/bin/env python
# new_post.py
# derived from http://benjamincongdon.me/blog/2016/03/21/Jekyll-New-Post-Script/

from datetime import datetime

TEMPLATE = """\
---
layout:     post
title:      {0}
date:       {1}
tags:       {2}
---

"""

try:
    input = raw_input
except NameError:
    pass

if __name__ == "__main__":

    title = input("Title:\n")
    categories = input("Categories:\n")

    timestamp = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    datestamp = datetime.today().strftime("%Y-%m-%d")

    file_name = datestamp + "-" + "-".join(title.split(" ")).lower() + ".markdown"

    with open("_posts/" + file_name, "w+") as file:
        file.write(TEMPLATE.format(title, timestamp, categories))
