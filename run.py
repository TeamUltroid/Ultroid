from pyUltroid.functions.tools import translate
from threading import Thread
from yaml import safe_load
from glob import glob

All = glob("strings/strings/*.yml")4
en = "strings/strings/en.yml"
strings = safe_load(open(en, "r"))
All.remove(en)

Threads = []

for lang in All:
  name = lang.split("/")[-1].split(".")[0]
  try:
    cont = safe_load(open(lang, "r"))
  except Exception as er:
    print(lang, er)
    continue
  rema = list(strings.keys() - cont.keys()) 
  if rema:
    def func():
      newc = ""
      for key in rema:
        try:
          res = translate(strings[key], lang_tgt=name)
          newc += f'"{key}": "{res}"'
        except Exception as er:
          print(name, er)
          continue
        if newc:
          with open(lang, "w") as file:
            file.write(newc)
  
    thre = Thread(target=func)
    thre.start()
    Threads.append(thre)

for thr in Threads:
  thr.join()