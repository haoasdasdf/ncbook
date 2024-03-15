import time
import os
from datetime import datetime
from pathlib import Path
import json
import yaml

WKD = { 'Mon': 1, 'Tue': 2, 'Wed': 3, 'Thu': 4, 'Fri': 5, 'Sat': 6, 'Sun': 7 }


def to_file(text, file):
  with open(file, 'w', encoding='UTF-8') as f:
    f.write(text)

def get_day(date_str):
  try:
    dt = datetime.strptime(date_str, '%Y/%m/%d')
    # res = dt.weekday()
    # for k, v in WKD.items():
    #   if dt.weekday() == v: return k
    return dt.isoweekday()
  except Exception as e:
    print(e)
    return -1

def weekday_to_number(str):
  for k, v in WKD.items():
    if str == k: return v
  return -1

def get_want_list(filename):
  try:
    with open(filename, 'r', encoding='UTF-8') as f:
      data = f.read()
      if Path(filename).suffix in ['.json']:
        data = json.loads(data)
      elif Path(filename).suffix in ['.yaml', '.yml']:
        data = yaml.safe_load(data)
      else:
        return None

      for obj in data:
        if 'id' not in obj:
          return None
        if 'name' not in obj:
          return None
        if 'time' not in obj:
          return None
        for d in obj['time']:
          
          wkds = list(d.keys())
          tms = list(d.values())
          if len(wkds) != 1 or len(tms) != 1:
            return None
          if weekday_to_number(wkds[0]) == -1:
            return None
          for tm in tms[0]:
            datetime.strptime(tm, '%H:%M')
        if 'callan' in obj:
          if type(obj['callan']) is not list:
            return None
          for t in obj['callan']:
            datetime.strptime(t, '%H:%M')
      return data
  except Exception as e:
    return None
