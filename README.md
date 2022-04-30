# AutoWatch
### Setup:
    pip install -r requirements.txt
### .env example:
    COMPANY_NUMBER=123
    EMPLOYEE_NUMBER=10
    MY_EMPLOYEE_NUMBER=10
    PASSWORD=whatever
    START_TIME=0900
    END_TIME=1800
### Information about environment variables
+ MY_EMPLOYEE_NUMBER - your own employee number, a safety measure for the case where EMPLOYEE_NUMBER is different because you filled hours for a colleague.
+ START_TIME - the time you came to the office (default is 09:00)
+ END_TIME - the time you left the office (default is 18:00)
### Execution:
    python autowatch.py
