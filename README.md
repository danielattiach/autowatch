# AutoWatch
### Setup:
    pip install .
### .env example:
    COMPANY_NUMBER=123
    EMPLOYEE_NUMBER=10
    MY_EMPLOYEE_NUMBER=10
    PASSWORD=whatever
    START_TIME=0900
    END_TIME=1800
    AUTOMATIC_TIME_FRAME=True
    FILL_MONTH=7
    FILL_YEAR=2022
### Information about environment variables
+ MY_EMPLOYEE_NUMBER - your own employee number, a safety measure for the case where EMPLOYEE_NUMBER is different because you filled hours for a colleague.
+ START_TIME - the time you came to the office (default is 09:00)
+ END_TIME - the time you left the office (default is 18:00)
+ AUTOMATIC_TIME_FRAME - if True, it will fill in 9 hours from START_TIME (unless it's a half day, then it'll fill in 5 hours). If False, it'll just use END_TIME
+ FILL_YEAR, FILL_MONTH - optional variables for if you need to fill a specific month and not the current month
### Execution:
    python -m autowatch.app
