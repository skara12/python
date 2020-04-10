import json 

file = open("test.json", "r")

data = json.load(file)

keyfile = open("output.json","r")

keys = json.load(keyfile)

for d in data:
 ans = d["_source"]["layers"]["usb.capdata"].split(":")
 for hex in ans:
  dec = int(hex,16)
  if dec != 0:
   print keys[str(dec)]