import datetime
from datetime import timedelta, date

# TODO - need holiday calendar (country=US)
#  - https://github.com/zurichat/zc_plugin_company_holiday_calendar

def add_business_days(from_date, number_of_days):
    to_date = from_date
    while number_of_days:
       to_date += timedelta(1)
       if to_date.weekday() < 5: # i.e. is not saturday or sunday
           number_of_days -= 1
    return to_date

def previous_working_day(to_date, number_of_days):
    from_date = to_date
    while number_of_days:
       from_date -= timedelta(1)
       if from_date.weekday() > 4: # i.e. is saturday or sunday
           number_of_days += 1
    return from_date

# TODO - module not found error in Django
# import holidays
# def previous_working_day(check_day_, holidays=holidays.US()):
#     offset = max(1, (check_day_.weekday() + 6) % 7 - 3)
#     most_recent = check_day_ - datetime.timedelta(offset)
#     if most_recent not in holidays:
#         return most_recent
#     else:
#         return previous_working_day(most_recent, holidays)