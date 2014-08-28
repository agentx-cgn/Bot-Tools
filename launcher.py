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

import sys, subprocess, time, os, sys, json
from time import sleep

sys.dont_write_bytecode = True

from data import data

## the game path
pyrogenesis = "/Daten/Projects/Osiris/ps/trunk/binaries/system/pyrogenesis"
pyrogenesis = "/usr/games/0ad"

## csv data
analysis    = "/home/noiv/Desktop/0ad/analysis/"

##startup options
tester      = {"map": "Arcadia 02"}

# cmd0AD = [pyrogenesis, "-quickstart", "-mod=charts", "-autostart=aitest07", "-autostart-ai=1:hannibal"]
# cmd0AD = [pyrogenesis, "-quickstart", "-mod=charts", "-autostart=ai-village-00", "-autostart-ai=1:hannibal"]
# cmd0AD = [pyrogenesis, "-quickstart", "-autostart=ai-village-00", "-autostart-ai=1:hannibal"]
# cmd0AD = [pyrogenesis, "-quickstart", "-autostart=" + tester['map'], "-autostart-ai=1:hannibal"]

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

def writeTestData():
  fTest = open("/home/noiv/.local/share/0ad/mods/public/simulation/ai/hannibal/tester-data.js", 'w')
  fTest.truncate()
  fTest.write("var TESTERDATA = " + json.dumps(tester) + ";")
  fTest.close()

def killTestData():
  fTest = open("/home/noiv/.local/share/0ad/mods/public/simulation/ai/hannibal/tester-data.js", 'w')
  fTest.truncate()
  fTest.close()

def processMaps():

  proc0AD = None

  tester["OnUpdate"] = "print('#! terminate');"

  for mp in data["testMaps"] :

    tester["map"] = mp
    writeTestData()
    cmd0AD  = [pyrogenesis, "-quickstart", "-autostart=" + mp, "-autostart-ai=1:hannibal"]
    proc0AD = subprocess.Popen(cmd0AD, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    print "  > " + mp

    try:

      for line in iter(proc0AD.stdout.readline, b'') : 

        sline = line.strip() 

        if sline.startswith("#! terminate") :
          proc0AD.terminate()
          sleep(2)
          if proc0AD : proc0AD.wait()
          if proc0AD : proc0AD.kill()
          break

        else :
          pass
          # sys.stdout.write(line)

    except KeyboardInterrupt, e :
      if proc0AD : proc0AD.terminate()
      break

  print "done."

def launch():

  winX = 1520; winY = 20

  doWrite    = False
  curFileNum = None
  idWindow   = None

  proc0AD = None
  cmd0AD = [pyrogenesis, "-quickstart", "-autostart=" + tester['map'], "-autostart-ai=1:hannibal"]

  files["log"] = open("/home/noiv/Desktop/0ad/last.log", 'w')
  files["log"].truncate()


  def terminate() :
    if proc0AD : proc0AD.terminate()

  writeTestData()
  proc0AD = subprocess.Popen(cmd0AD, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

  try:

    for line in iter(proc0AD.stdout.readline, b'') :

      sline = line.strip() ## removes nl and wp
      files["log"].write(sline + "\n")

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

    args = sys.argv[1:]
  
    if len(args) == 0:
      print "  launching map: " + tester['map']
      launch()
    
    elif args[0] == "maps" :
      print "  processing maps..."
      processMaps()

    else:
      tester['map'] = args[0]
      print "  launching map: " + tester['map']
      launch()
    
    cleanup()
    print("\nBye\n")



