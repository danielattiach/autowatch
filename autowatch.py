import re
import logging
from datetime import datetime, date
from dotenv import load_dotenv
from os import path, environ
from enum import Enum, auto
from dataclasses import dataclass

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.expected_conditions import element_to_be_clickable


class MonthType(Enum):
    START = auto()
    END = auto()


@dataclass
class Month:
    value: int
    type: MonthType


class AutoWatch:

    def __init__(self):
        basedir = path.abspath(path.dirname(__file__))
        load_dotenv(path.join(basedir, '.env'))
        self.company_number = environ.get('COMPANY_NUMBER')
        self.employee_number = environ.get('EMPLOYEE_NUMBER')
        self.my_employee_number = environ.get('MY_EMPLOYEE_NUMBER')
        self.password = environ.get('PASSWORD')
        self.this_year = date.today().year
        self.start_month = Month(
            value=int(environ.get('START_MONTH', date.today().month - 1)),
            type=MonthType.START,
        )
        self.end_month = Month(
            value=int(environ.get('END_MONTH', date.today().month)),
            type=MonthType.END
        )
        self.start_time = environ.get('START_TIME', '0900')
        self.end_time = environ.get('END_TIME', '1800')
        self.max_date = int(environ.get('MAX_DATE', 20))
        self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 10)
        if self.employee_number != self.my_employee_number:
            answer = input('Employee number is not yours, continue? [y/n]: ')
            if answer != 'y':
                exit()

    def handle_month(self, month: Month):
        month_value = month.value or 12
        year = self.this_year
        if month.type == MonthType.START and month_value == 12:
            year = self.this_year - 1

        self.driver.find_element_by_css_selector(f'[name="year"] option[value="{year}"]').click()
        self.driver.find_element_by_css_selector(f'[name="month"] option[value="{month_value}"]').click()

    def close_browser(self):
        logging.basicConfig(filename=f'bot.log', level=logging.INFO)
        self.driver.close()
        logging.info(f'Closed session with {self.employee_number}')

    def wait_for_window_open(self, current_window_handles):
        index = 0
        while len(self.driver.window_handles) <= current_window_handles:
            print(f'Waiting for window to open {index}', end='\r')
            index += 1
        return self.driver.window_handles[-1]

    def start(self):
        self.driver.get('https://checkin.timewatch.co.il/punch/punch.php')
        company_number = self.driver.find_element_by_id('compKeyboard')
        employee_number = self.driver.find_element_by_id('nameKeyboard')
        password = self.driver.find_element_by_id('pwKeyboard')
        company_number.send_keys(self.company_number)
        employee_number.send_keys(self.employee_number)
        password.send_keys(self.password)
        password.send_keys(Keys.RETURN)
        self.fill_hours()

    def fill_hours(self):
        self.wait.until(element_to_be_clickable((By.CSS_SELECTOR, 'a[href^="/punch/editwh.php"]'))).click()
        for month in (self.start_month, self.end_month):
            self.handle_month(month)
            self.wait.until(element_to_be_clickable((By.CSS_SELECTOR, 'table table')))
            tds = (self.driver.find_elements_by_css_selector('table table')[-1]
                   .find_elements_by_css_selector('td[bgcolor="red"]'))
            while tds:
                td = tds[0]
                row = td.find_element_by_xpath('..')
                row_date = datetime.strptime(re.findall(r'\d*-\d*-\d*', row.text)[0], '%d-%m-%Y')
                if (
                    row_date.year == self.this_year and
                    row_date.month >= self.end_month.value and
                    row_date.day > self.max_date
                ):
                    break
                self.fill_hours_for_row(td)
                self.driver.switch_to.window(self.driver.window_handles[0])
                self.driver.refresh()
                tds = (self.driver.find_elements_by_css_selector('table table')[-1]
                       .find_elements_by_css_selector('td[bgcolor="red"]'))
        self.close_browser()

    def fill_hours_for_row(self, row):
        current_window_handles = len(self.driver.window_handles)
        row.click()
        new_window_handle = self.wait_for_window_open(current_window_handles)
        self.driver.switch_to.window(new_window_handle)
        self.driver.find_element_by_xpath('//*[@id="ehh0"]').send_keys(self.start_time)
        self.driver.find_element_by_xpath('//*[@id="xhh0"]').send_keys(self.end_time)
        self.driver.find_element_by_css_selector('input[src="/images/update.jpg"]').click()


autowatch = AutoWatch()
autowatch.start()
