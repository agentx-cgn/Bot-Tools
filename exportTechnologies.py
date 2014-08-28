#!/usr/bin/env python
# -*- coding: utf-8 -*-

## improve: http://stackoverflow.com/questions/1871524/convert-from-json-to-csv-using-python
## http://trac.wildfiregames.com/browser/ps/trunk/source/tools/templatesanalyzer/unitTables.py

import numpy as np
import xml.etree.ElementTree as ET
import sys, os, glob, json

sys.dont_write_bytecode = True

folders = [
  ["", "all"],
  ["carthaganians/", "cart"],
  ["celts/", "celt"],
  ["hellenes/", "hele"],
  ["mauryans/", "maur"],
  ["persians/", "pers"],
  ["romans/", "roma"],
  ["successors/", ""],
]


def floatOrString(param) :
  try :
    return float(param)
  except :
    return param


if __name__ == '__main__':

  print
  trunk = '/Daten/Projects/Osiris/ps/trunk'
  rootExport = '/home/noiv/.local/share/0ad/mods/public/simulation/ai/hannibal/explorer/data/'
  rootTechnologies = trunk + '/binaries/data/mods/public/simulation/data/technologies/'
  dataExports = {}
  fileExport  = rootExport + "tech-json.export"
  counter = 0

  for f in folders : 

    folder = rootTechnologies + f[0]
    civ = f[1]

    print folder

    for fileTech in glob.glob(folder + '*.json') : 

      tech = fileTech.split("/")[-1].split(".")[0]
      print fileTech

      with open(fileTech, 'r') as content_file:
        data = json.loads(content_file.read())

      dataExports[tech] = data
      dataExports[tech]['civilisation'] = civ
      counter += 1


  f = open(fileExport, 'w')
  f.truncate()
  jsonExport = json.dumps(dataExports, sort_keys=True, indent=2) ## , ensure_ascii=False)
  f.write("var TECHNOLOGIES  = " + jsonExport + ";")
  f.close()

  print "wrote %s technologies to '%s' ~%s bytes" % (counter, fileExport, len(jsonExport))
  print jsonExport[:400]
  print

  print "done"
  print