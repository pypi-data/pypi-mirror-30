"""
tags used by lightswitch to determine power on/off behavior for a given EC2 instance.

At this time, only

   lightswitch:offhours

is defined.
"""

import re
from dateutil import parser

class BadTagError(ValueError):
    """Wrap value exception in project custom error"""
    pass

class ControlTags(object):
    """tagged EC2 info and state"""

    MODE_OFFONLY='leaveoff' # ? better than 'offonly' ?
    MODE_TOGGLE='toggle'

    TAGNAME_HOURS='lightswitch:offhours'
    TAGNAME_MODE='lightswitch:offmode'
    TAGNAME_DAYS='lightswitch:offdays'

    @classmethod
    def explain_tags(cls, body):
        """ return usage string containing tag names, formats """
        s = """
            lightswitch:offhours=21:00-7:00
            lightswitch:offhours=21:00-23:00

            lightswitch:offmode=toggle
            lightswitch:offmode=offonly

            lightswitch:offdays=sat,sun
            lightswitch:offdays=monday
        """
        return s

    @classmethod
    def get_target_tag_name(cls):
        """return the default offhours tag name. (DRY)"""
        return 'lightswitch:offhours'

    @classmethod
    def _parse_csvbody(cls, bodystr):
        """ take AWS tag body as CSV string, parse into dict.
        e.g. start=19:00,end=07:00"""
        body = {}
        items = bodystr.split(',')
        regex = re.compile(r'\s*(?P<key>\w+)\s*=\s*(?P<value>.*)')
        for i in items:
            match = regex.match(i)
            if match and match.group('key'):
                body[match.group('key').lower()] = match.group('value')
            else:
                raise BadTagError("bad CSV string: " + i)
        return body

    @classmethod
    def _parse_time(cls, timestr):
        timeval = parser.parse(timestr)
        return timeval.time()

    @classmethod
    def parse_offhours(cls, body):
        """ take AWS tag body, parse into start, end times"""
        range_dict = cls._parse_csvbody(body)
        start = cls._parse_time(range_dict['start'])
        end = cls._parse_time(range_dict['end'])
        return start, end

    @classmethod
    def time_is_within_range(cls, start, end, time):
        """ does the given time fall within the supplied range? """
        if start < end:
            return time >= start and time <= end

        # if end time smaller than start, assume the clock has 'wrapped',
        # e.g. 10pm to 7am, so check time is after s or before e
        return time >= start or time <= end

    @classmethod
    def parse_offmode(cls, body):
        """ take AWS tag body, parse into mode """
        mode = body.lower()
        if mode != cls.MODE_OFFONLY and mode != cls.MODE_TOGGLE:
            raise BadTagError("invalid mode: " + i + ", valid values are " +
                    cls.MODE_OFFONLY + " and " + cls.MODE_TOGGLE)
        return mode

    @classmethod
    def parse_offdays(cls, body):
        """ take AWS tag body, parse into list of days off.
        format is from DateTime weekday() where mon=0, ... sunday = 6,
        duplicates are dropped"""
        seen={}
        day_name_list = body.lower().split(',')
        for day_name in day_name_list:
            day_num=parser.parse(day_name).weekday()
            seen[day_num]=day_num

        return list(seen.keys())

    @classmethod
    def date_matches_an_offday(cls, offdaylist, date_to_test):
        """ does the supplied date hit an enumerated off day?
        If there are no off days (empty list), return false"""
        dow_to_test = date_to_test.weekday()
        return dow_to_test in offdaylist
