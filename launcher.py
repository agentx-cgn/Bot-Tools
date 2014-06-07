#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
https://docs.python.org/2/library/subprocess.html#popen-objects
http://stackoverflow.com/questions/1606795/catching-stdout-in-realtime-from-subprocess
http://askubuntu.com/questions/458041/find-x-window-name
http://stackoverflow.com/questions/9681959/how-can-i-use-xdotool-from-within-a-python-module-script
http://manpages.ubuntu.com/manpages/trusty/en/man1/avconv.1.html

xwininfo gives window info: xwininfo: Window id: 0x2800010 "0 A.D."

xdotool: 
  sudo apt-get install  libx11-dev  libxtst-dev libXinerama-dev
  make 
  make install

https://github.com/nullkey/glc/wiki/Capture

glc-capture --start --fps=30 --resize=1.0 --disable-audio --out=pyro.glc ./launcher.py
glc-play pyro.glc -o - -y 1 | avconv  -i -  -an -y pyro.mp4
avconv -i pyro.mp4 -codec copy -ss 15 -y pyro01.mp4
qt-faststart pyro01.mp4 pyro02.mp4
mplayer pyro02.mp4

'''

VERSION = "0.1.0"

import subprocess, time, os, sys

pyrogenesis = "/Daten/Projects/Osiris/ps/trunk/binaries/system/pyrogenesis"
cmd0AD = [pyrogenesis, "-quickstart", "-mod=charts", "-autostart=aitest07", "-autostart-ai=1:hannibal"]

files = {}

def findWindow(title) :
  process = subprocess.Popen("xdotool search --name '%s'" % (title), stdout=subprocess.PIPE, shell="FALSE")
  windowid = process.stdout.readlines()[0].strip()
  process.stdout.close()
  return windowid

def xdotool(command) :
  subprocess.call(("xdotool %s" % command).split(" "))

def cleanup() :
  for k, v in files.iteritems() : v.close()

def launch():

  doWrite = False
  curFileNum = None
  idWindow = None

  winX = 1520
  winY = 20

  proc0AD = None

  def terminate() :
    if proc0AD    : proc0AD.terminate()


  proc0AD = subprocess.Popen(cmd0AD, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

  try:

    for line in iter(proc0AD.stdout.readline, b'') :

      sline = line.strip() ## removes nl and wp

      if sline.startswith("#! terminate") :
        print(sline)
        terminate()
        return

      elif sline.startswith("#! xdotool init") :
        idWindow = findWindow("0 A.D")
        print("#! xdotool init %s" % idWindow)
        xdotool("windowmove %s %s %s" % (idWindow, winX, winY))

      elif sline.startswith("#! xdotool ") :
        params = " ".join(sline.split(" ")[2:])
        print("   X11: " + params)
        xdotool(params)

      elif sline.startswith("#! clear") :
        print(sline)
        sys.stderr.write("\x1b[2J\x1b[H") ## why not ??

      elif sline.startswith("#! open ") :
        filenum  = sline.split(" ")[2]
        filename = sline.split(" ")[3]
        files[filenum] = open(filename, 'w')
        files[filenum].truncate()
        # print(": open %s %s " % (filenum, filename))

      elif sline.startswith("#! append ") :
        filenum  = sline.split(" ")[2]
        dataLine = ":".join(sline.split(":")[1:])
        # print(": append %s %s " % (filenum, dataLine))
        files[filenum].write(dataLine + "\n")

      elif sline.startswith("#! write ") :
        print(sline)
        filenum  = sline.split(" ")[2]
        filename = sline.split(" ")[3]
        files[filenum] = open(filename, 'w')
        files[filenum].truncate()
        curFileNum = filenum
        
      elif sline.startswith("#! close ") :
        print(sline)
        filenum  = sline.split(" ")[2]
        files[filenum].close()    

      # elif doWrite :
      #   # sys.stdout.write(".") little feedback if needed
      #   files[curFileNum].write(line)

      else :
        sys.stdout.write(line)

  except KeyboardInterrupt, e :
    terminate()

if __name__ == '__main__':
    launch()
    cleanup()
    print("\nBye\n")



