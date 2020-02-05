import re
import logging
from datetime import datetime, date
from dotenv import load_dotenv
from os import path, environ

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.expected_conditions import element_to_be_clickable


class AutoWatch:

    def __init__(self):
        basedir = path.abspath(path.dirname(__file__))
        load_dotenv(path.join(basedir, '.env'))
        self.company_number = environ.get('COMPANY_NUMBER')
        self.employee_number = environ.get('EMPLOYEE_NUMBER')
        self.password = environ.get('PASSWORD')
        self.start_month = int(environ.get('START_MONTH', date.today().month - 1))
        self.end_month = int(environ.get('END_MONTH', date.today().month))
        self.start_time = environ.get('START_TIME', '0900')
        self.end_time = environ.get('END_TIME', '1800')
        self.max_date = int(environ.get('MAX_DATE', 20))
        self.driver = webdriver.Chrome()
        self.wait = WebDriverWait(self.driver, 10)

    def close_browser(self):
        logging.basicConfig(filename=f'bot.log', level=logging.INFO)
        self.driver.close()
        logging.info(f'Closed session with {self.employee_number}')

    @staticmethod
    def get_element(driver, xpath=None, class_name=None):
        if not class_name:
            try:
                return driver.find_element_by_xpath(xpath)
            except:
                return None
        else:
            try:
                return driver.find_element_by_class_name(class_name)
            except:
                return None

    @staticmethod
    def wait_to_click(element):
        in_view = False
        while not in_view:
            try:
                element.click()
                in_view = True
            except:
                pass

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
            self.wait.until(element_to_be_clickable((By.CSS_SELECTOR,
                                                     f'[name="month"] option[value="{month}"]'))).click()
            self.wait.until(element_to_be_clickable((By.CSS_SELECTOR, 'table table')))
            tds = (self.driver.find_elements_by_css_selector('table table')[-1]
                   .find_elements_by_css_selector('td[bgcolor="red"]'))
            while len(tds) > 0:
                td = tds[0]
                row = td.find_element_by_xpath('..')
                row_date = datetime.strptime(re.findall(r'\d*-\d*-\d*', row.text)[0], '%d-%m-%Y')
                if row_date.month >= self.end_month and row_date.day > self.max_date:
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
