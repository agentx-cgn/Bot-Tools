#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
http://stackoverflow.com/questions/1606795/catching-stdout-in-realtime-from-subprocess
https://docs.python.org/2/library/subprocess.html#popen-objects
'''

VERSION = "0.1.0"

import subprocess, time, os, sys

pyrogenesis = "/Daten/Projects/Osiris/ps/trunk/binaries/system/pyrogenesis"

proc = [pyrogenesis, "-quickstart", "-mod=charts", "-autostart=aitest07", "-autostart-ai=1:hannibal"]


files = {}

def cleanup() :
  for k, v in files.iteritems() :
    # print("\nclosing: " + k)
    v.close()

def launch():

  doWrite = False
  curFileNum = None

  process = subprocess.Popen(proc, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

  try:

    for line in iter(process.stdout.readline, b'') :

      sline = line.strip() ## removes nl and wp

      if sline.startswith("#! terminate") :
        print(sline)
        process.terminate()
        return

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
    ## Ctrl-c
    pass

if __name__ == '__main__':
    launch()
    cleanup()
    print("\nBye\n")



