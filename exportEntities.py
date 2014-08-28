#!/usr/bin/env python
# -*- coding: utf-8 -*-

## improve: http://stackoverflow.com/questions/1871524/convert-from-json-to-csv-using-python
## http://trac.wildfiregames.com/browser/ps/trunk/source/tools/templatesanalyzer/unitTables.py

import numpy as np
import xml.etree.ElementTree as ET
import sys, os, glob, json

sys.dont_write_bytecode = True

exports = [
  "units",
  "structures",
  "rubble",
  "other",
  "gaia",
]

nodes = [
  "Builder/Entities",
  "Classes",
  "Cost/BuildTime",
  "Cost/Resources/food",
  "Cost/Resources/wood",
  "Cost/Resources/metal",
  "Cost/Resources/stone",
  "Cost/Population",
  "Cost/PopulationBonus",
  "Footprint/Square@width",
  "Footprint/Square@depth",
  "Identity/Civ",
  "Identity/SpecificName",
  "Identity/RequiredTechnology",
  "GarrisonHolder/Max",
  "GarrisonHolder/List",
  "Health/Max",
  "Heal/Range",
  "Heal/HP",
  "Obstruction/Static@width",
  "Obstruction/Static@depth",
  "Obstruction/Unit@radius",
  "ProductionQueue/Entities",
  "ResourceSupply/Amount",
  "ResourceSupply/Type",
  "ResourceGatherer/BaseSpeed",
  "ResourceDropsite/Types",
  "TerritoryInfluence/Radius",
  "TerritoryInfluence/Weight",
  "UnitMotion/WalkSpeed",
  "UnitMotion/Run/Speed",
  "Vision/Range",
]

def floatOrString(param) :
  try :
    return float(param)
  except :
    return param

def readTemplate(root, pathfileTemplate, existing=None):

  data = {}
  tpl  = ET.parse(root + pathfileTemplate)
  
  if (tpl.getroot().get("parent") != None):
    data = readTemplate(root, tpl.getroot().get("parent") + ".xml", data)
  
  def setIf(tpl, node, default="") :
    
    val = None
    
    if node.find("@") > -1 : 
      attr = node.split("@")
      if tpl.find("./" + attr[0]) != None and tpl.find("./" + attr[0]).attrib.has_key(attr[1]) : 
        val = floatOrString(tpl.find("./" + attr[0]).attrib[attr[1]])
        
    else :
      if tpl.find("./" + node) != None : 
        if tpl.find("./" + node).attrib.has_key("datatype") :
          val = tpl.find("./" + node).text
          if val :
            val = val.replace("\n", " ")
            val = [ t for t in val.split(" ") if len(t)]
        else : 
          val = floatOrString(tpl.find("./" + node).text)
    
    if val != None and val != 0.0:
      data[node] = val

  def setClasses(tpl) :

    if (tpl.find("./Identity/VisibleClasses") != None):
      newClasses = tpl.find("./Identity/VisibleClasses").text.split(" ")
      for elem in newClasses:
        if (elem.find("-") != -1):
          newClasses.pop(newClasses.index(elem))
          if elem in data["Classes"]:
            data["Classes"].pop(newClasses.index(elem))
      data["Classes"] += newClasses
    
    if (tpl.find("./Identity/Classes") != None):
      newClasses = tpl.find("./Identity/Classes").text.split(" ")
      for elem in newClasses:
        if (elem.find("-") != -1):
          newClasses.pop(newClasses.index(elem))
          if elem in data["Classes"]:
            data["Classes"].pop(newClasses.index(elem))
      data["Classes"] += newClasses


  for node in nodes : 
    if node == 'Classes' :
      if not data.has_key("Classes") : data['Classes'] = []
      setClasses(tpl)
      data["Classes"] = [i.strip() for i in data["Classes"]]
      data["Classes"] = filter(lambda i : len(i.strip()), data["Classes"])
    else :
      setIf(tpl, node, "")
  
  return data


if __name__ == '__main__':

  print
  trunk = '/Daten/Projects/Osiris/ps/trunk'
  rootExport = '/home/noiv/.local/share/0ad/mods/public/simulation/ai/hannibal/explorer/data/'
  rootTemplates = trunk + '/binaries/data/mods/public/simulation/templates/'

  for export in exports : 

    dataExports = {}
    pathExports = rootTemplates + export + "/"
    templates   = glob.glob(pathExports + '*.xml')
    fileExport  = rootExport + export + "-json.export"

    for template in templates :
      pathfile = "/".join(template.split("/")[-2:])
      dataExports[pathfile[:-4]] = readTemplate(rootTemplates, pathfile)

    f = open(fileExport, 'w')
    f.truncate()
    jsonExport = json.dumps(dataExports, sort_keys=True, indent=2)
    f.write("var " + export.upper() + " = " + jsonExport + ";")
    f.close()

    print "wrote %s %s to '%s' ~%s bytes" % (len(templates), export.upper(), export, len(jsonExport))
    # print jsonExport[:400]
    # print

  print "done"
  print