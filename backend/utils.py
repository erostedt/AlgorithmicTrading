from datetime import datetime


def convert_timestamp_to_datetime(timestamp):
    """
    Converter from timestamp unit to datetime unit.
    :param timestamp: Timestamp to be converted.
    :return: Datetime object.
    """
    timestamp_length = len(str(timestamp))
    if timestamp_length == 10:
        return datetime.strptime(str(timestamp), '%Y-%m-%d')
    if timestamp_length == 19:
        return datetime.strptime(str(timestamp), '%Y-%m-%d %H:%M:%S')
    elif timestamp_length == 25:
        dt = datetime.strptime(str(timestamp)[:19], '%Y-%m-%d %H:%M:%S')
        ####
        # Not 100% sure this works...!
        sign = str(timestamp)[19]
        hour_shift = datetime.strptime(str(timestamp)[20:], '%H:%M').hour
        minute_shift = datetime.strptime(str(timestamp)[20:], '%H:%M').minute
        if sign == "+":
            hour_shift *= -1
            minute_shift *= -1
        dt = datetime.replace(dt, hour=(dt.hour + hour_shift) % 24, minute=(dt.minute + minute_shift)%60)
        ####
        return dt
    else:
        print("Wrong format/lengths! The length of the timestamp is " + str(timestamp_length) + ". Only 10, 19 and 25 currently allowed.")


def convert_datetime_to_timestamp(_datetime):
    """
    Converts datetime object to timestamp.
    :param _datetime: Datetime object to be converted.
    :return: Timestamp unit.
    """
    return datetime.strftime(_datetime, '%Y-%m-%d %H:%M:%S')


def factorial(n):
    fac = 1
    for i in range(1, n+1):
        fac *= i
    return int(fac)
