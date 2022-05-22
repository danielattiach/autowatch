import re
import time
import requests
from dataclasses import dataclass
from datetime import datetime, date
from urllib.parse import urlparse, parse_qs

from bs4 import BeautifulSoup
from bs4.element import Tag

from autowatch.config import Config
from autowatch.data import HEADERS, DATA


@dataclass
class Row:
    html: Tag
    hours_to_add: int
    current_date: date


class AutoWatch:
    def __init__(self):
        self.config = Config()
        self.session = requests.Session()
        self.login_soup = None
        self.punch_page = None
        self.punch_page_month = self.config.fill_month
        self.punch_page_year = self.config.fill_year
        self.ixemplee = None
        self.rows = []
        self.skip_dates = set()

    def login(self):
        response = self.session.post('https://c.timewatch.co.il/user/validate_user.php', data={
            'comp': self.config.company_number,
            'name': self.config.employee_number,
            'pw': self.config.password,
        })
        self.config.cookies['PHPSESSID'] = self.session.cookies.get('PHPSESSID')
        self.login_soup = BeautifulSoup(response.text, 'html.parser')

    def set_referer_header(self):
        link = next(
            link for link in self.login_soup.find_all('a', {'class': 'new-link'}) if 'עדכון נתוני נוכחות' in link.text
        )
        parsed_url = urlparse(link.get('href'))
        params = parse_qs(parsed_url.query)
        self.punch_page_year = self.punch_page_year or params['y'][0]
        self.punch_page_month = self.punch_page_month or params['m'][0]
        self.ixemplee = params['ee'][0] if params.get('ee') else ''
        HEADERS['referer'] = (
            'https://c.timewatch.co.il/punch/editwh.php'
            f'?ee={self.ixemplee}&e={self.config.company_number}&m={self.punch_page_month}&y={self.punch_page_year}'
        )

    def setup(self):
        DATA['c'] = self.config.company_number
        self.login()
        self.set_referer_header()
        self.get_punch_page()
        DATA['e'] = self.ixemplee
        DATA['tl'] = self.ixemplee

    def get_punch_page(self, force_refresh=False):
        if self.punch_page is None or force_refresh:
            self.punch_page = self.session.get(
                f'https://c.timewatch.co.il/punch/editwh.php',
                params={
                    'ee': str(self.ixemplee),
                    'e': self.config.company_number,
                    'm': self.punch_page_month,
                    'y': self.punch_page_year,
                }
            )
            DATA['csrf_token'] = re.search(r'var csrf_token="(.*)";', self.punch_page.content.decode()).group(1)
            self.filter_dates()
        return self.punch_page

    def filter_dates(self):
        self.rows = []
        soup = BeautifulSoup(self.punch_page.text, 'html.parser')
        for row in soup.find_all('tr', {'class': 'update-data'}):
            if 'חסרה כניסה/יציאה' in row.text:
                match = re.search(r'(\d{2}-\d{2}-\d{4})', row.text)
                if not match:
                    continue
                current_date = datetime.strptime(
                    re.search(r'(\d{2}-\d{2}-\d{4})', row.text).group(1), '%d-%m-%Y'
                ).date()
                if current_date.strftime(self.config.date_format) in self.skip_dates:
                    continue
                self.rows.append(Row(
                    html=row,
                    current_date=current_date,
                    hours_to_add=int(re.search(rf'{current_date.strftime("%d-%m-%Y")}.*(\d):\d\d', row.text).group(1)),
                ))

    def submit_hours(self):
        if DATA['d'] in self.skip_dates:
            return
        # TimeWatch is a hella weird, if you do things too fast it just doesn't process some dates
        print(f'Trying to set {DATA["d"]} to {DATA["ehh0"]}:{DATA["emm0"]} - {DATA["xhh0"]}:{DATA["xmm0"]}')
        time.sleep(0.25)
        res = self.session.post(
            'https://c.timewatch.co.il/punch/editwh3.php',
            cookies=self.config.cookies,
            headers=HEADERS,
            data=DATA,
        )
        if res.text == 'limited punch':
            print(f'Unable to set {DATA["d"]}. Probably a bug on TimeWatch, please verify manually')
            self.skip_dates.add(DATA['d'])

    def submit_hours_for_missing_dates(self, retries=0):
        if retries > 10:
            print('I tried 10 times and you still have missing dates, I give up. Maybe you should try again later.')
            return

        for row in self.rows:
            DATA['ehh0'] = self.config.start_time_hour
            DATA['emm0'] = self.config.start_time_minute
            DATA['xhh0'] = (
                str(int(self.config.start_time_hour) + row.hours_to_add)
                if self.config.automatic_time_frame else self.config.end_time_hour
            )
            DATA['xmm0'] = self.config.end_time_minute
            DATA['d'] = row.current_date.strftime(self.config.date_format)

            self.submit_hours()

        # check if there are still missing dates
        self.get_punch_page(force_refresh=True)
        if self.rows:
            print(f'You still have {len(self.rows)} missing dates, I will try again in 3 seconds.')
            time.sleep(3)
            self.submit_hours_for_missing_dates(retries=retries + 1)

    def play(self):
        self.setup()
        if self.config.my_employee_number and self.config.employee_number != self.config.my_employee_number:
            answer = input('You seem to be filling hours for someone else. Are you sure you want to continue? [y/n] ')
            if answer.lower() == 'n':
                print('Aborting.')
                return

        self.submit_hours_for_missing_dates()
