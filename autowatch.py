import re
import logging
from time import sleep
from datetime import datetime, date
from random import uniform

from dotenv import load_dotenv
from os import path, environ
from enum import Enum, auto
from dataclasses import dataclass

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.expected_conditions import element_to_be_clickable, invisibility_of_element_located


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
            value=date.today().month - 1,
            type=MonthType.START,
        )
        self.end_month = Month(
            value=date.today().month,
            type=MonthType.END,
        )
        self.start_time = environ.get('START_TIME', '0900')
        self.end_time = environ.get('END_TIME', '1800')
        self.max_date = 20
        self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 5)
        if self.employee_number != self.my_employee_number:
            answer = input('Employee number is not yours, continue? [y/n]: ')
            if answer != 'y':
                exit()

    def approve_reminder_popup(self):
        wait = WebDriverWait(self.driver, 3)
        try:
            wait.until(element_to_be_clickable((By.CSS_SELECTOR, '[id="jqi_state0_buttonקראתי"]'))).click()
        except TimeoutException:
            pass

    def handle_month(self, month: Month):
        month_value = month.value or 12
        year = self.this_year
        if month.type == MonthType.START and month_value == 12:
            year = self.this_year - 1

        sleep(uniform(1, 2))
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
        self.driver.get('https://c.timewatch.co.il/punch/punch.php')
        self.login()
        self.fill_hours()

    def login(self):
        company_number = self.driver.find_element_by_id('login-comp-input')
        employee_number = self.driver.find_element_by_id('login-name-input')
        password = self.driver.find_element_by_id('login-pw-input')
        company_number.send_keys(self.company_number)
        employee_number.send_keys(self.employee_number)
        password.send_keys(self.password)
        password.send_keys(Keys.RETURN)
        self.approve_reminder_popup()
        self.wait.until(element_to_be_clickable((By.CSS_SELECTOR, '.edit-info .new-link'))).click()

    def fill_hours(self):
        for month in (self.start_month, self.end_month):
            self.handle_month(month)
            self.wait.until(element_to_be_clickable((By.CSS_SELECTOR, '.table-responsive')))
            tds = (self.driver.find_element_by_css_selector('.table-responsive')
                   .find_elements_by_css_selector('td[style]'))
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
                self.driver.refresh()
                table = self.wait.until(element_to_be_clickable((By.CSS_SELECTOR, '.table-responsive')))
                tds = table.find_elements_by_css_selector('td[style]')
        self.close_browser()

    def fill_hours_for_row(self, td):
        td.click()
        sleep(uniform(0, 2))
        self.wait.until(element_to_be_clickable((By.CSS_SELECTOR, '.modal-popup-body .portlet-body')))
        self.driver.find_element_by_xpath('//*[@id="ehh0"]').send_keys(f'{self.start_time}{self.end_time}')
        self.driver.find_element_by_css_selector('.modal-popup-btn-confirm').click()
        self.wait.until(invisibility_of_element_located((By.CSS_SELECTOR, '.modal-popup-body')))
        sleep(uniform(1, 3))


if __name__ == '__main__':
    autowatch = AutoWatch()
    try:
        autowatch.start()
    except:  # noqa
        print('Something went wrong, closing browser')
        autowatch.close_browser()
