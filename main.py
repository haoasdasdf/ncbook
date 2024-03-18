
import logging

from logging.handlers import TimedRotatingFileHandler
import sys
import argparse
import os

import utils.nc as nc
from  utils.tools import *
from utils.settings import userdata_dir

logger = logging.getLogger()
for h in logger.handlers:
    logger.removeHandler(h)

h = logging.StreamHandler(sys.stdout)
rt = TimedRotatingFileHandler('ncbook.log', when='D', interval=1, backupCount=5)

FORMAT = '%(levelname)s %(asctime)s [%(filename)s:%(lineno)d] [%(funcName)s] %(message)s'
h.setFormatter(logging.Formatter(FORMAT))
rt.setFormatter(logging.Formatter(FORMAT))

logger.addHandler(h)
logger.addHandler(rt)

logger.setLevel('INFO')


# ua = UserAgent('edge')

# userdata_dir = './userdata'

# BASE_URL = 'https://nativecamp.net'
# LOGIN_PATH = '/login'
# FAVOURiTE_PATH = '/favorite'
# TEACHER_PATH = '/waiting/detail/'
# COIN_PATH = '/coin'

# WKD = { 'Mon': 1, 'Tue': 2, 'Wed': 3, 'Thu': 4, 'Fri': 5, 'Sat': 6, 'Sun': 7 }


test_list = [
  # {
  #   'id': 40766,
  #   'name': 'Iva',
  #   'time': [
  #     {'Mon': ['22:00', '22:30', '23:00']},
  #     {'Tue': ['22:00', '22:30', '23:00']},
  #     {'Wed': ['22:00', '22:30', '23:00']},
  #     {'Fri': ['22:00', '22:30', '23:00']},
  #     {'Sat': ['22:00', '22:30', '23:00']},
  #     {'Sun': ['22:00', '22:30', '23:00']},
  #   ]
  # }
  {
    'id':42391,
    'name': 'Eva',
    'time': [
      {'Mon': ['23:30']},
      {'Tue': ['23:30']},
      {'Wed': ['23:30']},
      {'Fri': ['23:30']},
      {'Sat': ['23:30']},
      {'Sun': ['23:30']},
    ]
  }
  # {
  #   'id': 152916,
  #   'name': 'Linda',
  #   'time': [
  #     {'Mon': ['12:00', '22:30', '23:00', '23:30']},
  #     {'Tue': ['12:00', '22:30', '23:00', '23:30']},
  #     {'Wed': ['12:00', '22:30', '23:00', '23:30']},
  #     {'Thu': ['19:30']},
  #     {'Fri': ['12:00', '22:30', '23:00', '23:30']},
  #     {'Sat': ['12:00', '22:30', '23:00', '23:30']},
  #     {'Sun': ['12:00', '22:30', '23:00', '23:30']},
  #   ]
  # }
  #   {
  #   'id': 145629,
  #   'name': 'Halli',
  #   'time': [
  #     {'Mon': ['22:00', '22:30', '23:00', '23:30']},
  #     {'Tue': ['22:00', '22:30', '23:00', '23:30']},
  #     {'Wed': ['22:00', '22:30', '23:00', '23:30']},
  #     {'Thu': ['19:00']},
  #     {'Fri': ['22:00', '22:30', '23:00', '23:30']},
  #     {'Sat': ['22:00', '22:30', '23:00', '23:30']},
  #     {'Sun': ['22:00', '22:30', '23:00', '23:30']},
  #   ]
  # },
]

USER = os.environ.get('nc_uid')
PW = os.environ.get('nc_pw')

def check(tc_list, need_book=False):
  auto = nc.NC(USER, PW, userdata_dir, need_book)
  for tc in tc_list:
    auto.teacher = tc['name']
    auto.tid = tc['id']

    availables = auto.check_schedule(tc)
    # availables = {'2024/03/05': ['09:30', '12:30', '17:00', '17:30', '18:00', '18:30', '19:00', '19:30', '20:00', '20:30', '21:00', '21:30'], '2024/03/06': ['09:30', '10:00', '10:30', '11:00', '11:30', '12:00', '12:30', '13:00', '14:30', '15:00', '15:30', '16:00', '16:30', '17:00', '17:30', '18:00', '18:30', '19:00', '19:30', '20:00', '20:30', '21:00'], '2024/03/07': ['09:30', '10:00', '10:30', '11:00', '11:30', '12:00', '12:30', '13:00', '14:30', '15:00', '15:30', '16:00', '16:30', '17:00', '17:30', '18:00', '19:00', '19:30', '20:00', '20:30', '21:00'], '2024/03/04': ['17:30', '18:00', '18:30', '19:00', '19:30', '20:00', '20:30', '21:00']}
    if availables is None:
      return
    logger.info(F'{auto.teacher} availables: {availables}')
    tasks = auto.create_tasks(tc['time'], availables)
    # tasks = auto.check_bookable(tc)
    if len(tasks) > 0:
      logger.info(F'{auto.teacher} can book: {tasks}')
      logger.info(F'tasks: { tasks}')
      for task in tasks:
        callan = False
        if tc.get('callan') and task.get('time') in tc.get('callan'):
          callan = True
        logger.info(F'is callan {callan}')
        res = auto.book(task, callan=callan)
        # if res == 1:
          # logger.info(F'succeed in booking {auto.teacher} {task["date"]} {task["time"]}')
        if res == 0:
          logger.warning(F'failed to book {auto.teacher} {task["date"]} {task["time"]}')
        elif res == -1:
          logger.error('something wrong')
    else:
      logger.info(F'{auto.teacher} availables: {len(tasks)}')

def supervisor(tc_list, sec, need_book=False):
  auto = nc.NC(USER, PW, userdata_dir, need_book)
  for tc in tc_list:
    auto.teacher = tc['name']
    auto.tid = tc['id']
    while True:
      availables = auto.check_schedule(tc)
      # availables = {'2024/03/05': ['09:30', '12:30', '17:00', '17:30', '18:00', '18:30', '19:00', '19:30', '20:00', '20:30', '21:00', '21:30'], '2024/03/06': ['09:30', '10:00', '10:30', '11:00', '11:30', '12:00', '12:30', '13:00', '14:30', '15:00', '15:30', '16:00', '16:30', '17:00', '17:30', '18:00', '18:30', '19:00', '19:30', '20:00', '20:30', '21:00'], '2024/03/07': ['09:30', '10:00', '10:30', '11:00', '11:30', '12:00', '12:30', '13:00', '14:30', '15:00', '15:30', '16:00', '16:30', '17:00', '17:30', '18:00', '19:00', '19:30', '20:00', '20:30', '21:00'], '2024/03/04': ['17:30', '18:00', '18:30', '19:00', '19:30', '20:00', '20:30', '21:00']}
      logger.info(F'{auto.teacher} availables: {availables}')
      tasks = auto.create_tasks(tc['time'], availables)
      if len(tasks) > 0:
        logger.info(F'{auto.teacher} can book: {tasks}')
        logger.info(F'tasks: { tasks}')
        for task in tasks:
          callan = False
          if tc.get('callan') and task.get('time') in tc.get('callan'):
            callan = True
          logger.info(F'is callan {callan}')
          res = auto.book(task, callan=callan)
          # if res == 1:
          #   logger.info(F'succeed in booking {auto.teacher} {task["date"]} {task["time"]}')
          if res == 0:
            logger.warning(F'failed to book {auto.teacher} {task["date"]} {task["time"]}')
          elif res == -1:
            logger.error('something wrong')
      else:
        logger.info(F'{auto.teacher} availables: {len(tasks)}')
      time.sleep(sec)


if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('input', help='input a want list filename')
  parser.add_argument('-b', '--book', help='book or test')
  parser.add_argument('-s', '--supervise', type=int, help='supervise interval seconds')

  args = parser.parse_args()
  
  if args.input:
    obj = get_want_list(args.input)
    if obj:
      if args.book == 'book':
        logger.info('book mode')
        need_book = True 
      else:
        logger.info('test mode')
        need_book = False

      if args.supervise:
        try:
          logger.info(F'supervise mode interval {args.supervise}')
          supervisor(obj, args.supervise, need_book=need_book)
        except:
          logger.error(F'bad supervise interval, please input number of seconds')
      else:
        logger.info('one time mode')
        check(obj, need_book)
    else:
      logger.error(F'please check file format and contents {args.input}')
  else:
      logger.error('please check your book list')

