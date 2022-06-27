# common/dates.py
import holidays
import datetime
from datetime import timedelta, date
from common.models import CompanyHoliday

# TODO - need holiday calendar (country=US)
#  - https://github.com/zurichat/zc_plugin_company_holiday_calendar

def add_business_days(from_date, number_of_days=1):
    to_date = from_date
    while number_of_days:
       to_date += timedelta(1)
       if to_date.weekday() < 5: # i.e. is not saturday or sunday
           number_of_days -= 1
    return to_date

def previous_working_day(to_date, number_of_days=1):
    if to_date is None:
        return None
    from_date = to_date
    while number_of_days:
       from_date = to_date - timedelta(number_of_days)
       if from_date.weekday() < 5: # i.e. is saturday or sunday
            break
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

def workdays_us(m, y = date.today().year):
    # now = datetime.datetime.now()
# TODO
    cc_holidays = [ CompanyHoliday.objects.filter(year=y).values_list('holiday', flat=True) ]

    us_holidays = holidays.US(subdiv='CA')  # this is a dict / FIXME CA and other region...

    businessdays = 0
    for i in range(1, 32):
        try:
            thisdate = datetime.date(y, m, i)
        except(ValueError):
            break
        if thisdate.weekday() < 5 and thisdate not in us_holidays: # Monday == 0, Sunday == 6 
            if not thisdate in cc_holidays:
                businessdays += 1

    return businessdays