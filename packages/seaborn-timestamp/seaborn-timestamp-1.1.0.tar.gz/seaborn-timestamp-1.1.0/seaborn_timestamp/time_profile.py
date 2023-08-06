""" This will record the timing of message calls per gevent thread.

    Basic Usage is at the beginning of the event such as an API call
        # this will create the thread message that will store all future messages

        TimeProfile.message("your text here", create=True)

        # this will end the timing call, otherwise it is ended at the next time_message
        TimeProfile.message("your text here",done=True)

        # this will generate a dictionary report and should be done when all done
        TimeProfile.report()

    Report:
        overhead # an estimate of how much time the time_profile took
        thread_id # the id of the gevent thread
        start # the time of the create time message
        end # the time of the time_report
        messages # a list of dict of message reports
            Function # the function that made the time_message call
            Line Number # the line number that made the time_message
            Message # the str of the message
            Start # the first time the time message was called for this message
            End # the last time the time message was called for this message
            Count # the number of times this message was called
            Min # the smallest amount of time for a message cycle
            Max # the largest amount of time for a message cycle
            Avg # the average amount of time for a message cycle
            Sum # the total amount of time for all message cycles
            Times # a list of time cycles

        *Note Line Number and count will not be modified for a time_message with a done= True
        """
__author__ = 'Ben Christenson'
__date__ = "4/23/15"

from time import time as get_time
import gevent
import logging

log = logging.getLogger(__name__)
from seaborn_meta.calling_function import function_info
from seaborn_table.table import SeabornTable


class TimeProfile(object):
    ACTIVE_PROFILES = {}    # {thread_id, TimeProfile}
    SIGNIFICANT_DIGITS = 4  # number of digits to report in the report
    MAX_PROFILES = 50       # max number of threads before testing max time
    MAX_TIME = 10 * 60      # max time of a thread when culling
    ACTIVE = True           # if this is false all messages will instantly return

    def __init__(self, thread_id, start):
        self.thread_id = thread_id or self._get_thread_id()
        self.messages = {}
        self.order = []
        self.overhead = 0
        self.start = start
        self.end = start
        self.previous = None

    @classmethod
    def message(cls, message='', done=False, create=False, thread_id=None,
                     function_name=None, function_index=-1, line_number=None, log_message=True):
        try:
            if not cls.ACTIVE:
                return
            now = get_time()
            thread_id = thread_id or cls._get_thread_id()
            if create:
                cls.ACTIVE_PROFILES[thread_id] = cls(thread_id, now)
                cls._clean_active_profiles(now)

            if thread_id in cls.ACTIVE_PROFILES:
                time_thread = cls.ACTIVE_PROFILES[thread_id]
                message = str(message)

                if message not in time_thread.messages:
                    info = function_info(function_index, function_name, line_number)
                    time_message = TimeMessage(info['function_name'], info['line_number'], message, now,
                                               time_thread.start)
                    time_thread.messages[message] = time_message
                    time_thread.order.append(message)
                else:
                    assert done is False, "Attempting to end message that has never started"
                    time_message = time_thread.messages[message]

                if log_message:
                    log.debug(str(time_message))

                if time_thread.previous is not None:
                    time_thread.previous.update(now)

                if time_message is not time_thread.previous or not done:
                    time_message.update(now, done)

                time_thread.previous = time_message
                if not done:
                    time_thread.overhead += get_time() - now
            elif log_message:
                log.debug(str(message) + " (done)" * done)
        except Exception as e:
            log.error("Exception in time_profile.time_message: %s" % e, exc_info=True)

    def report(self):
        self.end = get_time()
        if self.previous.end <= self.previous.start:
            self.previous.update(get_time(), True)

        return {'Overhead': self.overhead,
                'Thread_id': self.thread_id,
                'Start': self.start,
                'End': self.end,
                'Messages': [self.messages[o].report(self.SIGNIFICANT_DIGITS) for o in self.order]}


    @classmethod
    def report_table(cls, thread_id=None, columns=None):
        report = cls.time_report(thread_id)
        if not report:
            return ''
        columns = columns or ['Function', 'Line Number', 'Message', 'Start', 'End', 'Count', 'Min', 'Max', 'Avg', 'Sum']
        table = SeabornTable(report['Messages'], columns=columns)
        return table

    @classmethod
    def time_report(cls, thread_id=None):
        try:
            thread_id = thread_id or cls._get_thread_id()
            if thread_id in cls.ACTIVE_PROFILES:
                return cls.ACTIVE_PROFILES.pop(thread_id).report()
            return []
        except Exception as e:
            log.error("Exception in time_profile.time_report: %s" % e, exc_info=True)
            raise e

    @classmethod
    def decorator(cls, function):
        def decorated_func(*args, **kwargs):
            try:
                cls.message(message=function.__name__, done=False, function_name=function.__name__,
                             line_number=function.func_code.co_firstlineno)
            except Exception as e:
                log.error("Exception in time_profile.time_profile_decorator: %s" % e, exc_info=True)

            function(*args, **kwargs)

            try:
                cls.message(message=function.__name__, done=True, function_name=function.__name__,
                             line_number=function.func_code.co_firstlineno)
            except Exception as e:
                log.error("Exception in time_profile.time_profile_decorator: %s" % e, exc_info=True)

        decorated_func.__name__ = function.__name__ + '_decorated'
        return decorated_func

    def __str__(self):
        return 'Thread_ID: %s Overhead: %s\n\n%s' % (str(self.thread_id).ljust(20),
                                                     round(self.overhead, self.SIGNIFICANT_DIGITS),
                                                     self.report_table())

    @staticmethod
    def _get_thread_id():
        return id(gevent.getcurrent())

    @classmethod
    def _clean_active_profiles(cls, now):
        if len(cls.ACTIVE_PROFILES) < cls.MAX_PROFILES:
            return
        for k, v in cls.ACTIVE_PROFILES.items():
            if (now - v.start) > cls.MAX_TIME:
                cls.ACTIVE_PROFILES.pop(k)


class TimeMessage(object):
    def __init__(self, function, line_number, message, now, thread_start):
        self.function = function
        self.line_number = line_number
        self.message = str(message)
        self.thread_start = thread_start
        self.start = now
        self.end = now
        self.last_start = now
        self.times = []

    def update(self, now, done=None):
        if done is False:
            self.last_start = now
        else:
            time_diff = now - self.last_start
            self.end = now
            if done is True and self.times:
                self.times[-1] = time_diff
            elif done or time_diff >= 0.0:
                self.times.append(time_diff)

    def report(self, significant_digits):
        def r(num):
            return round(num, significant_digits)

        ret = {'Function': self.function,
               'Line Number': self.line_number,
               'Message': self.message,
               'Start': r(self.start - self.thread_start),
               'End': r(self.end - self.thread_start),
               'Count': len(self.times),
               'Times': [r(t) for t in self.times], }

        if self.times:
            ret.update({
                'Min': r(min(self.times)),
                'Max': r(max(self.times)),
                'Avg': r(1.0 * sum(self.times) / len(self.times)),
                'Sum': r(min(self.end - self.start, sum(self.times))), })
        else:
            ret.update({'Min': '',
                        'Max': '',
                        'Avg': '',
                        'Sum': '', })
        return ret

    def __str__(self):
        return 'TimeMessage: "%s" for function %s at %s' % (self.message, self.function, self.end)
