# AutoWatch
### Setup:
    brew cask install chromedriver
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
### .env example:
    COMPANY_NUMBER = 123
    EMPLOYEE_NUMBER = 10
    PASSWORD = whatever
    START_MONTH = 1
    END_MONTH = 2
    START_TIME = 0800
    END_TIME = 1700
    MAX_DATE = 10
### Information about environment variables
+ START_MONTH - the month from which we start auto filling (default is last month)
+ END_MONTH - the month in which we stop auto filling (default is the current month)
+ START_TIME - the time you came to the office (default is 09:00)
+ END_TIME - the time you left the office (default is 18:00)
+ MAX_DATE - what day in the end month should be the last when auto filling (default is 20)
### Execution:
    source venv/bin/activate
    python autowatch.py
