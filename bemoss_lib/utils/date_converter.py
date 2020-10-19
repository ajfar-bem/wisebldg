__author__ = 'rajee'
import pytz
import datetime
#TODO read this from settings file
import settings
import time

UTC = pytz.UTC
bemoss_tmzone = pytz.timezone(settings.TIME_ZONE)

def tzNow(): #gives timezone aware now
    return datetime.datetime.now().replace(tzinfo=bemoss_tmzone)

def localToUTC(local_date):
    #Convert Local-time to UTC
    if local_date.tzinfo == None:
        local_date = bemoss_tmzone.normalize(bemoss_tmzone.localize(local_date))
    utc_dt = local_date.astimezone(pytz.utc)
    utc_dt = utc_dt.replace(tzinfo=None)
    return utc_dt

def UTCToLocal(UTC_date):
    #Convert UTC to Local
    UTC_dt = UTC_date.replace(tzinfo=pytz.utc)
    local_dt = UTC_dt.astimezone(bemoss_tmzone)
    return local_dt

def toLocal(user_date):
    return user_date.astimezone(bemoss_tmzone)

def serializeDate(date):
    return str(date.strftime('%Y-%m-%d %H:%M:%S:%f') + "*" + str(date.tzinfo))

def deserialize(date):
    dttimestr, tz = date.split('*')
    dt = datetime.datetime.strptime(dttimestr,'%Y-%m-%d %H:%M:%S:%f')
    if tz != "None":
        tz = pytz.timezone(tz)
        return tz.localize(dt)
    else:
        return dt
