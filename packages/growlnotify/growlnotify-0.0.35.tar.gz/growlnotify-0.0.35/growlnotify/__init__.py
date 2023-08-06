#!/usr/bin/env python
# -*- coding: utf-8 -*-
from fullpath import fullpath
from isstring import isstring
import only
from subopen import subopen
from public import public


def open_app():
    returncode, _, _ = subopen(["killall", "-s", "Growl", "Growl 2"])
    if returncode != 0:
        returncode, _, stderr = subopen(["open", "-a", "Growl 2"])
        if returncode != 0:
            raise OSError(stderr)

# known errors:
# We failed to notify after succesfully registering
# fix Failed to register with
# ----
# 1) different versions produce diffrent errors
# 2) pirate versions contains additional errors
# repeat few until 0 exit status


def run(args, stdin):
    i = 0
    while i < 50:
        returncode, _, stderr = subopen(args, stdin=stdin)
        if returncode == 0:
            return
        if not (stderr.find("Failed to register with") >=
                0 or stderr.find("failed to notify") >= 0):
            return
        i += 1


def format_title(value):
    if value and not isstring(value):
        value = str(value)
    if value and value[0] == "-":
        value = "\\" + value
    return value


def format_message(value):
    if not value:
        value = ""
    if value and not isstring(value):
        value = str(value)
    return value


@only.osx
@public
def growlnotify(title=None, message=None, app=None,
                sticky=False, icon=None, image=None, url=None):
    title = format_title(title)
    message = format_message(message)
    args = []
    if title:
        args += ["-t", title]
    if app:
        args += ["-a", app]
    if icon:
        args += ["--icon", icon]
    if image:
        args += ["--image", fullpath(image)]
    if sticky:
        args += ["-s"]
    if url:
        args += ["--url", url]
    stdin = message
    # need first growlnotify arg for correct app icon
    args = ["growlnotify"] + args
    open_app()
    run(args, stdin)
