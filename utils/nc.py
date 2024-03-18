import json
import logging
import os
import sys
# from bs4 import BeautifulSoup
# import requests
# from useragent_changer import UserAgent
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time
import os
from datetime import datetime, timedelta


from os.path import join, dirname
from dotenv import load_dotenv

from utils.tools import *
from utils.settings import *

load_dotenv(verbose=True)

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

logger = logging.getLogger()
for h in logger.handlers:
    logger.removeHandler(h)

h = logging.StreamHandler(sys.stdout)

FORMAT = '%(levelname)s %(asctime)s [%(filename)s:%(lineno)d] [%(funcName)s] %(message)s'
h.setFormatter(logging.Formatter(FORMAT))
logger.addHandler(h)

logger.setLevel('INFO')

class NC():
  def __init__(self, uid, pw, udir=None, need_book=False) -> None:
    self.wait_time = 5
    self.teacher = ''
    self.tid = 0

    self.uid = uid
    self.pw = pw
    self.need_book = need_book

    options = webdriver.ChromeOptions()
    # options.add_argument('--headless=new')
    options.add_argument('--no-sandbox')
    if udir:
      options.add_argument('--user-data-dir=' + udir)
    # options.add_experimental_option("detach", True)
    self.browser = webdriver.Chrome(options=options)

    self.wait = WebDriverWait(self.browser, self.wait_time)

  def __del__(self):
    self.browser.quit()
    pass

  def test(self):
    html_file = os.getcwd() + '/' + 'table-linda.html'
    logger.info(html_file)
    self.browser.get('file:///' + html_file)
    to_file(self.browser.page_source, 'table.html')
    logger.info(self.browser.title)
    slots = self.browser.find_elements(By.XPATH, '//a[@data-status="available"]')
    # logger.info(slots)

    for slot in slots:
      weekday = get_day(slot.get_attribute('data-date'))
      start_time = slot.get_attribute('data-time')
      for des in tc_list[0]['time']:
        wkd = list(des.keys())[0]
        time_slots = list(des.values())[0]
        if weekday == weekday_to_number(wkd)  and start_time in time_slots:
          logger.info(weekday, start_time)
          slot.click()

  def login(self, user, pw):
    url = BASE_URL + LOGIN_PATH
    self.browser.get(url)
    if 'ログイン' not in self.browser.title:
      logger.info(self.browser.title)
      return False
    # input login form
    if not user or not pw or not len(user) or not len(pw):
      logger.error('please check your username password')
      return False
    username_input = self.browser.find_element(By.ID, 'UserEmail')
    password_input = self.browser.find_element(By.ID, 'UserPassword')
    login_button = self.browser.find_element(By.ID, 'login-btn')
    username_input.clear()
    username_input.send_keys(user)
    password_input.clear()
    password_input.send_keys(pw)
    login_button.click()
    
    if 'マイページ' in self.browser.title:
      return True
    logger.info(self.browser.title)
    return False

  def check_coin(self):
    try:
      coin = self.browser.find_element(By.XPATH, '//span[@class="header_cnt_coin" and @id="header_cnt_coin"]')
      coin = coin.text.replace(',', '')
      logger.info(coin)
      return int(coin)
    except NoSuchElementException:
      logger.info('need login')
      return -1
    except Exception as e:
      logger.error(e)
      return -999




  def check_schedule(self, tc):
    url = BASE_URL + TEACHER_PATH + str(tc['id'])
    self.browser.get(url)
    coin_res = self.check_coin()
    if not coin_res >= int(MINIMUN_COIN):
      if coin_res >= 0:
        logger.warning(F'coin is not enough {coin_res}')
      elif coin_res == -1:
        login_res = self.login(self.uid, self.pw)
        if not login_res:
          logger.error('login failed')
          return None
        self.browser.get(url)
        coin_res = self.check_coin()
        if not coin_res >= int(MINIMUN_COIN):
          if coin_res == -1:
            logger.error('login failed')
            return None
          elif coin_res == -999:
            logger.error('get coin failed unknown 2')
            return None
      elif coin_res == -999:
        logger.error('get coin failed unknown 1')
        return None

    try:
      self.wait.until(EC.visibility_of_element_located((By.XPATH, '//table[@id="teacher_reserve_table"]')))
      # to_file(self.browser.page_source,F'teacher-{tc["name"]}.html')
      table = self.browser.find_element(By.XPATH, '//table[@id="teacher_reserve_table"]')
      # to_file(table.get_attribute('innerHTML'),F'table-{tc["name"]}.html')
      slots = table.find_elements(By.XPATH, '//a[@data-status="available"]')
    except Exception as e:
      logger.info(e)
      logger.info(F'get table time failed for {tc["name"]}')
    a_slots = {}
    for slot in slots:
      if a_slots.get(slot.get_attribute('data-date')) is None:
        a_slots[slot.get_attribute('data-date')] =[slot.get_attribute('data-time')]
      else:
       a_slots[slot.get_attribute('data-date')].append(slot.get_attribute('data-time'))
    return a_slots

  def check_bookable(self, tc):
    url = BASE_URL + TEACHER_PATH + str(tc['id'])
    self.browser.get(url)
    coin_res = self.check_coin()
    if not coin_res >= int(MINIMUN_COIN):
      if coin_res >= 0:
        logger.warning(F'coin is not enough {coin_res}')
      elif coin_res == -1:
        login_res = self.login(self.uid, self.pw)
        if not login_res:
          logger.error('login failed')
          return None
        self.browser.get(url)
        coin_res = self.check_coin()
        if not coin_res >= int(MINIMUN_COIN):
          if coin_res == -1:
            logger.error('login failed')
            return None
          elif coin_res == -999:
            logger.error('get coin failed unknown 2')
            return None
      elif coin_res == -999:
        logger.error('get coin failed unknown 1')
        return None

    try:
      today = datetime.now()
      today_dt = today.strftime('%Y/%m/%d')
      c_wkd = {}
      tasks = []
      for i in range(0, 7):
        d = today + timedelta(i)
        ds = d.strftime('%Y/%m/%d')
        logger.info(d)
        # logger.info(get_day(ds))
        # c_wkd[d.strftime('%Y/%m/%d')] = get_day(ds)
        # for dt
      # logger.info(c_wkd)
        for des in tc['time']:
          wkd = list(des.keys())[0]
          time_slots = list(des.values())[0]
          # logger.info(wkd)
          # logger.info(time_slots)
          if weekday_to_number(wkd) == get_day(ds):
            for ts in time_slots:
              try:
                self.wait.until(EC.visibility_of_element_located((By.XPATH, '//table[@id="teacher_reserve_table"]')))
                # to_file(self.browser.page_source,F'teacher-{tc["name"]}.html')
                table = self.browser.find_element(By.XPATH, '//table[@id="teacher_reserve_table"]')
                # to_file(table.get_attribute('innerHTML'),F'table-{tc["name"]}.html')
                slots = table.find_elements(By.XPATH, '//a[@data-status="available"]')
                # slot = self.wait.until(EC.visibility_of_element_located((By.XPATH, F'//a[@data-date="{ds}" and @data-time= "{ts}"]')))
                slot = table.find_element(By.XPATH, F'//a[@data-date="{ds}" and @data-time= "{ts}"]')
                if slot.get_attribute('data-status') == 'available':

                  tasks.append(
                            {
                            'date': ds,
                            'time': ts
                            }
                          )
                else:
                  logger.info(F'slot {ds} {ts} is not available')
              except TimeoutException:
                logger.info(F'cannot find slot for {ds} {ts}')
              except Exception as e:
                logger.info(F'get error for checking {ds} {ts}')
                logger.error(e)
      logger.info(tasks)
      return tasks
    

    except Exception as e:
      logger.info(e)
      logger.info(F'check_bookable failed for {tc["name"]}')

  def create_tasks(self, my_time, free_slots):
    tasks = []
    for des in my_time:
      wkd = list(des.keys())[0]
      time_slots = list(des.values())[0]
      # logger.info(wkd)
      # logger.info(time_slots)
      for fk, fv in free_slots.items():
        if weekday_to_number(wkd) == get_day(fk):
          logger.debug(fk)
          for t in time_slots:
            for v in fv:
                if t == v:
                  tasks.append(
                    {
                    'date': fk,
                    'time': v
                    }
                  )
    return tasks

  def book(self, task, callan=False):
    self.browser.get(BASE_URL + TEACHER_PATH + str(self.tid))
    if '講師詳細' not in self.browser.title:
      logger.error(F'wrong page for booking {self.browser.title}')
      return -1
    dd = task['date']
    dt = task['time']
    try:
      table = self.wait.until(EC.visibility_of_element_located((By.XPATH, '//table[@id="teacher_reserve_table"]')))
      # slot = self.browser.find_elements(By.XPATH, F'//a[@data-status="available" and @data-date="{dd}" and @data-time= "{dt}"]')
      slot = self.wait.until(EC.visibility_of_element_located((By.XPATH, F'//a[@data-date="{dd}" and @data-time= "{dt}"]')))
      if not slot.get_attribute('data-status') == 'available':
        logger.warning(F'slot not available')
      slot.click()
      navi_tab = self.wait.until(EC.visibility_of_element_located((By.XPATH, '//div[@class="tbs-wrap category"]')))
      # to_file(self.browser.page_source, F'navi-{tc["name"]}.html')
      
      # textbook_tab = self.browser.find_element(By.XPATH, '//div[@display-flag="1" and @text-book-category-id="119"]')
      if callan:
        textbook_tab = self.wait.until(EC.visibility_of_element_located((By.XPATH, '//div[not(contains(@class, "hide")) and @class-eng="Callan Method"]')))
      else:
        textbook_tab = self.wait.until(EC.visibility_of_element_located((By.XPATH, '//div[not(contains(@class, "hide")) and @class-eng="Selection of teaching materials after entering the lesson room"]')))
      textbook_tab.click()
      logger.info('textbook_tab.click')
      # to_file(self.browser.page_source, F'textbook-{self.teacher}.html')
      # self.browser.implicitly_wait(2)
      # chapter_tab = textbook_tab.find_elements(By.XPATH, '//li[@chapter-id="1"]')
      if callan:
        chapter_tab = self.wait.until(EC.visibility_of_element_located((By.XPATH, '//li[@chapter-id="102"]')))
      else:
        chapter_tab = self.wait.until(EC.visibility_of_element_located((By.XPATH, '//li[@chapter-id="1"]')))
      chapter_tab.click()
      logger.info('chapter_tab.click')
      # to_file(self.browser.page_source, F'chapter-{self.teacher}.html')

      next_btn = self.wait.until(EC.visibility_of_element_located((By.XPATH, '//a[@data-status="available" and @id="chooseReservedSchedule"]')))
      next_btn.click()
      logger.info('next_btn.click')
      # to_file(self.browser.page_source, F'next_btn-{self.teacher}.html')
      date_time=F'{slot.get_attribute("data-date")} {slot.get_attribute("data-time")}'
      # logger.info(F'//a[@date-time="{date_time}" and @id="saveReservedSchedule"]')
      confirm_btn = self.wait.until(EC.visibility_of_element_located((By.XPATH, F'//a[@date-time="{date_time}" and @data-substitute_teacher_flg="1"  and @id="saveReservedSchedule"]')))
      to_file(self.browser.page_source, F'confirm_btn-{self.teacher}.html')
      if self.need_book:
        confirm_btn.click()
        logger.info('confirm_btn.click')
        to_file(self.browser.page_source, F'confirm_btn-after-{self.teacher}{datetime.now().strftime("%Y%m%d_%H%M%S")}.html')
        close_btn = self.wait.until(EC.visibility_of_element_located((By.XPATH, F'//a[@class="btn_style btn_gray close_modal" and @href="#" and contains(text(), "閉じる")]')))
        close_btn.click()
        logger.info('close_btn.click')
        to_file(self.browser.page_source, F'close_btn-after-{self.teacher}-{datetime.now().strftime("%Y%m%d_%H%M%S")}.html')
      # to_file(self.browser.page_source, F'confirm_btn-after-{self.teacher}.html')
        logger.info(F'book finished {self.teacher} {dd} {dt}')
      else:
        logger.info(F'test finished {self.teacher} {dd} {dt}')
    except TimeoutException as e:
      logger.error(F'cannot find element {e}')
      to_file(self.browser.page_source, F'failed-{self.teacher}-{datetime.now().strftime("%Y%m%d_%H%M%S")}.html')
      return 0
    return 1


  