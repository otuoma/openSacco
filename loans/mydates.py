#!/usr/bin/env python3
# -*- py-which-shell: "python3"; python: "python3" -*-

# Copyright (c) 2015 Frank Sergeant
# MIT license (see LICENSE file or http://pygmy.utoh.org/amort/LICENSE)
# frank@pygmy.utoh.org

import sys
sys.path.append('')
import datetime


ONEDAY = datetime.timedelta(days=1)
# This timedelta object can be added to the most recent quote to find
# the next day for fetching new quotes.

ONEYEAR = 365 * ONEDAY

def dateFromString (str):
    '''Given a string such as "2011-11-02", convert it to a date object'''
    y, m, d = [int(i) for i in str.split("-")]
    return datetime.date (y,m,d)

def stringFromDate (date):
    '''Given a datetime.date, convert it to a string such as "2011-11-02"'''
    y, m, d = (date.year, date.month, date.day)
    return "%s-%s-%s" % (y, m,d)
    # return "%04d-%02d-%02d" % (y, m, d)

def shortdate (date):
    '''Given a datetime.date, convert it to a short string
       representing string such as "12/14", "12/21", or "12/28".
    '''
    y, m, d = (date.year, date.month, date.day)
    return "%s/%s" % (m, d)
    # return "%02d/%02d" % (m, d)

def tupleFromDate(date):
    '''Given a datetime.date, convert it to a (yyyy,mm,dd) tuple.
    '''
    return date.year, date.month, date.day


def dateFromTuple(ymdTuple):
    '''Given a (y,m,d) tuple, return a datetime.date.
    '''

    y, m, d = ymdTuple

    return datetime.date(y, m, d)


def today():
    return datetime.date.today()

def weekend (date):
    '''Return true if date is a Saturday or Sunday'''
    return date.isoweekday() > 5

def asDate (date):
    if type(date) is str:
        date = dateFromString (date)
    return date

def beginningOfYear (date):
    '''Given a date, return a new date with the same year but with
       01-01 for the month and day.
    '''
    date = asDate (date)
    y, m, d = (date.year, date.month, date.day)
    newdate = datetime.date (y, 1, 1)
    return newdate


EARLY = dateFromString ("1947-01-14")   # earlier than any date I will ever need
LATE  = dateFromString ("2150-12-31")   # later than any date I will ever need


def dateRangeStr(startDate, endDate):
    '''Return a string appropriately describing the date range.  This is a helper
       method used by various account reports.
    '''
    startDate = asDate (startDate)
    endDate = asDate (endDate)
    if (startDate == EARLY) and (endDate == LATE):
        result = ""
    elif startDate == EARLY:
        result = "(through %s)" % endDate
    elif endDate == LATE:
        result = "(from %s)" % startDate
    else:
        result = "(%s through %s)" % (startDate, endDate)
    return result

def daysBetween(startDate, endDate):
    '''Return the datetime.timedelta, so 
       dayBetween("2005-01-01", "2005-12-31") --> 364 days
    '''
    startDate = asDate (startDate)
    endDate = asDate (endDate)
    return (endDate - startDate).days

def daysBetweenInclusive(startDate, endDate):
    '''Return the inclusive datetime.timedelta, so 
       dayBetween("2005-01-01", "2005-12-31") --> 365 days
    '''
    return daysBetween (startDate, endDate) + 1


# ##############################################################
# Functions to return a series of dates    
# ##############################################################

def weeklyDates (fromDate, toDate):
    '''Return a series of weekly ending dates inclusively from the
       given fromDate through the toDate.
    '''
    sevendays = 7 * ONEDAY
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    result = []
    nextDate = asDate (fromDate)
    lastDate = asDate (toDate)

    while nextDate <= lastDate:
        #print ("(nextDate, lastDate) = (%s %s, %s)" % (nextDate, days[nextDate.weekday()], lastDate))
        result.append (nextDate)
        nextDate = nextDate + sevendays
    return result


def monthlyDates (fromDate, toDate):
    '''Return a series of month ending dates inclusively from the
       given fromDate through the toDate.  For example, if the
       fromDate is "1995-04-30" and the toDate is "1995-09-30" then
       the series would be ["1995-04-30", "1995-05-31", "1995-06-30",
       "1995-08-31", "1995-09-30"].  The beginning and ending dates
       must be month-end dates.
    '''
    #              Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec
    maxMonthDays = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    result = []
    nextDate = asDate (fromDate)
    lastDate = asDate (toDate)
    year  = nextDate.year
    month = nextDate.month
    day   = nextDate.day

    while nextDate <= lastDate:
        #print ("(nextDate, lastDate) = (%s, %s)" % (nextDate, lastDate))
        result.append (nextDate)
        month = month + 1
        if month == 13:
            month = 1
        if month == 1:
            year = year + 1
        try:
            nextDate = datetime.date (year, month, maxMonthDays[month - 1])
        except:
            # this happens whenever month is Feb and year is not a leap year
            nextDate = datetime.date (year, month, 28)
    #weekday = start.weekday()  # gives the index of the week where 0=Monday, 1=Tuesday, ..., 6=Sunday
    #weekday2 = start.isoweekday()  # Sunday is 7 and Monday is 1

    return result

def quarterlyDates (fromDate, toDate):
    '''Return a series of quarterly ending dates inclusively from the
       given fromDate through the toDate.  For example, if the
       fromDate is "1995-03-31" and the toDate is "1995-09-30" then
       the series would be ["1995-03-31", "1995-06-30", "1995-09-30"].
       The beginning and ending dates must be month-end dates.
    '''
    #              Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec
    maxMonthDays = [31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    result = []
    nextDate = asDate (fromDate)
    lastDate = asDate (toDate)
    year  = nextDate.year
    month = nextDate.month
    day   = nextDate.day

    while nextDate <= lastDate:
        #print ("(nextDate, lastDate) = (%s, %s)" % (nextDate, lastDate))
        result.append (nextDate)
        month = month + 3
        if month > 12:
            month = 3
        if month == 3:
            year = year + 1
        try:
            nextDate = datetime.date (year, month, maxMonthDays[month - 1])
        except:
            # this happens whenever month is Feb and year is not a leap year, which 
            # cannot happen for quarters, but leave it here anyway for now.
            nextDate = datetime.date (year, month, 28)
    return result

def yearlyDates (fromYear, toYear):
    '''Return a series of year ending dates inclusively from the
       given fromYear through the toYear.  E.g.,
          yearlyDates (1998, 2011)
    '''
    nextYear = fromYear

    result = []
    while nextYear <= toYear:
        result.append (datetime.date (nextYear, 12, 31))
        nextYear += 1
    return result

def addOneYear (dt):
    (y, m, d) = tupleFromDate(dt)
    return dateFromTuple ((y+1, m, d))

def subtractOneYear (dt):
    (y, m, d) = tupleFromDate(dt)
    return dateFromTuple ((y-1, m, d))

def subtractDays (dt, n):
    # back up n days from dt
    datetime.timedelta(days=n)
    return dt - datetime.timedelta(days=n)

def yesterday (dt=None):
    """ Answer the day before the dt (if given) else answer the day before today"""
    if dt is None:
        dt = today()
    return subtractDays (dt, 1)

def addOneMonth (dt):
    (y, m, d) = tupleFromDate(dt)
    m += 1
    if m > 12:
        m = 1
        y += 1
    return dateFromTuple ((y, m, d))

def addMonths (dt,n):
    (y, m, d) = tupleFromDate(dt)
    while n > 12:
        y += 1
        n -= 12
    m += n
    if m > 12:
        m = 1
        y += 1
    return dateFromTuple((y, m, d))


def isLeapYear (dt):
    y,_,_ = tupleFromDate (dt)
    divBy4 = (y % 4) == 0
    if not divBy4:
        return False
    divBy100 = (y % 100) == 0
    divBy400 = (y % 400) == 0

    if divBy100 and not divBy400:
        return False
    else:
        return True

def testLeapYear (dt):
    if isLeapYear (dt):
        print ("%s is a leap year" % dt)
    else:
        print ("%s is not a leap year" % dt)

def testLeapYears ():
    for dt in ["1996-03-10", "1998-06-30", "2000-01-01", "2001-02-02",
               "2002-03-03", "2003-04-04", "2004-05-05", "2014-01-14",
               "2015-01-14", "2016-01-14", "2100-01-14", "2104-01-14",
               "2200-09-11", "2400-10-12"]:

        testLeapYear (dateFromString (dt))
               
               
               # example
               # monthlyDatesFrom ("2011-01-31")
               # monthlyDatesFrom ("2010-01-31", "2011-12-31")
               
