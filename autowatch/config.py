import re
from os import getenv
from datetime import date
from dotenv import load_dotenv


class Config:
    date_format = '%Y-%m-%d'
    company_number = NotImplemented
    employee_number = NotImplemented
    my_employee_number = NotImplemented
    password = NotImplemented
    start_time_hour = NotImplemented
    start_time_minute = NotImplemented
    end_time_hour = NotImplemented
    end_time_minute = NotImplemented
    automatic_time_frame = NotImplemented
    fill_year = NotImplemented
    fill_month = NotImplemented
    cookies = NotImplemented

    def __init__(self):
        load_dotenv()
        self.cookies = {}
        self.company_number = getenv('COMPANY_NUMBER')
        self.employee_number = getenv('EMPLOYEE_NUMBER')
        self.my_employee_number = getenv('MY_EMPLOYEE_NUMBER')
        self.fill_year = getenv('FILL_YEAR')
        self.fill_month = getenv('FILL_MONTH')
        self.password = getenv('PASSWORD')
        self.automatic_time_frame = getenv('AUTOMATIC_TIME_FRAME', 'True').lower() == 'true'
        self.start_time_hour, self.start_time_minute = [
            string for string in re.split(r'(\d{2})', getenv('START_TIME', '0900'))
            if string.isdigit()
        ]
        self.end_time_hour, self.end_time_minute = [
            string for string in re.split(r'(\d{2})', getenv('END_TIME', '1800'))
            if string.isdigit()
        ]
