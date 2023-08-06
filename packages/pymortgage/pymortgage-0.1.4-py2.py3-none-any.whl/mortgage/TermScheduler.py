import datetime
# from future import print_statement


JSON_DATE_FORMAT = '%Y-%m-%d'


class WrongSchedule(Exception):
    def __init__(self, exception_txt):
        self.msg = exception_txt

    def __str__(self):
        return self.msg


class TermSchedule(object):
    def __init__(self, start_date, end_date, skip_last=False, **kwargs):
        self.start_date = start_date
        self.end_date = end_date
        self._skip_last = skip_last
        self._iter_class = TermSchedule_iter
        self._kwargs = kwargs
        self._annual_periods = None

    def __iter__(self):
        my_iterator = self._iter_class(
            self.start_date,
            self.end_date,
            self._skip_last,
            **self._kwargs)
        my_iterator.annual_periods = self.annual_periods
        return my_iterator

    def set_annual_periods(self, periods):
        self._annual_periods = int(periods)

    def get_annual_periods(self):
        return self._annual_periods

    annual_periods = property(fset=set_annual_periods, fget=get_annual_periods)


class TermSchedule_iter(object):
    """Term schedule"""

    def __init__(self, start_date, end_date, skip_last=False, **kwargs):
        self.start_date = start_date
        self.end_date = end_date
        self.current_date = self.start_date
        self.next_year = self._plus_year(self.start_date)
        if 'annual_periods' in kwargs:
            self._annual_periods = kwargs['annual_periods']
        else:
            self._annual_periods = None
        self._skip_last = skip_last
        # self._iter_class = TermSchedule_iter
        # self._iter_args = kwargs

    def _plus_year(self, from_year, years=1):
        """Caveat: do not use for Feb 29 - won't work as expected"""
        return datetime.date(from_year.year + years, from_year.month, from_year.day)

    def next_term(self, from_date):
        return from_date + self.get_delta()

    def set_annual_periods(self, periods):
        if periods is None:
            self._annual_periods = None
        else:
            self._annual_periods = int(periods)

    def get_annual_periods(self):
        return self._annual_periods

    annual_periods = property(fset=set_annual_periods, fget=get_annual_periods)

    def get_delta(self):
        pass

    def __iter__(self):
        return self

    def next(self):
        # next_date=self.start_date+self.get_delta()
        # print self.current_date, self.next_year
        if self.current_date > self.end_date:
            raise StopIteration
        elif self.current_date == self.end_date:
            return_date = self.current_date
            self.current_date = self.next_term(self.current_date)
            if self._skip_last:
                raise StopIteration
            else:
                return return_date
        else:
            return_date = self.current_date
            next_date = self.next_term(self.current_date)
            if next_date > self.end_date:
                next_date = self.end_date
                if self._skip_last:
                    raise StopIteration
            if next_date >= self.next_year:
                # self.current_date=self.next_year
                # self.next_year=self._plus_year(self.next_year)
                self.current_date = next_date
                self.next_year = self._plus_year(self.next_year)
            else:
                self.current_date = next_date
            return return_date


class CustomSchedule(TermSchedule):
    def __init__(self, start_date, end_date, skip_last=False, **kwargs):
        self._events = kwargs['events']
        # self.annual_periods = kwargs['annual_periods']
        # kwargs['annual_periods'] = self.annual_periods
        super(CustomSchedule, self).__init__(start_date, end_date, skip_last, **kwargs)
        self.annual_periods = kwargs['annual_periods']
        self._iter_class = None

    def __iter__(self):
        return iter(self._events)


class WeeklySchedule(TermSchedule):
    def __init__(self, start_date, end_date, skip_last=False, **kwargs):
        weeks = kwargs['weeks']
        if 52 % weeks != 0:
            raise WrongSchedule(
                "Schedule does not fit into annual cycle: {0}wk annual {1}wk period".format(
                    52, weeks))
        self.annual_periods = 52 // weeks
        kwargs['annual_periods'] = self.annual_periods
        super(WeeklySchedule, self).__init__(start_date, end_date, skip_last, **kwargs)
        self._iter_class = WeeklySchedule_iter


class WeeklySchedule_iter(TermSchedule_iter):
    def __init__(self, start_date, end_date, skip_last=False, **kwargs):
        super(WeeklySchedule_iter, self).__init__(start_date, end_date, skip_last, **kwargs)
        weeks = kwargs['weeks']
        self.delta = datetime.timedelta(weeks=weeks)
        # self.annual_periods = 52 // weeks

    def get_delta(self):
        return self.delta


class MonthlySchedule(TermSchedule):
    def __init__(self, start_date, end_date, skip_last=False, **kwargs):
        months = kwargs['months']
        self.months = months
        if 12 % months != 0:
            raise WrongSchedule(
                "Schedule does not fit into annual cycle: {0}mo annual {1}mo period".format(
                    12, months))
        annual_periods = 12 // months
        kwargs['annual_periods'] = annual_periods
        super(MonthlySchedule, self).__init__(start_date, end_date, skip_last, **kwargs)
        self.annual_periods = annual_periods
        self._iter_class = MonthlySchedule_iter


class MonthlySchedule_iter(TermSchedule_iter):
    def __init__(self, start_date, end_date, skip_last=False, **kwargs):
        self.months = kwargs['months']
        super(MonthlySchedule_iter, self).__init__(start_date, end_date, skip_last, **kwargs)

    def next_term(self, from_date):
        next_year = from_date.year
        next_month = from_date.month + self.months
        next_day = from_date.day

        if next_month > 12:
            next_year = next_year + next_month // 12
            next_month = next_month % 12
        try:
            return_date = datetime.date(next_year, next_month, next_day)
        except ValueError as e:
            print("from_year: {0}, from_month: {1}, from_day: {2}".format(
                from_date.year, from_date.month, from_date.day))
            print(
                "next_year: {0}, next_month: {1}, next_day: {2}".format(
                    next_year, next_month, next_day))
            raise e
        return return_date


def monthly_schedule(start_date, years, step=1):
    from datetime import date
    return MonthlySchedule(start_date, date(start_date.year + years,
                                            start_date.month, start_date.day),
                           months=step, skip_last=True)


def weekly_schedule(start_date, years, step=2):
    from datetime import date
    return WeeklySchedule(start_date, date(start_date.year + years,
                                           start_date.month, start_date.day),
                          weeks=step, skip_last=True)


def date2json(event_date):
    """serialize date into string"""
    return event_date.strftime(JSON_DATE_FORMAT)


def json2date(date_string):
    """de-serialize date"""
    return datetime.datetime.strptime(date_string, JSON_DATE_FORMAT)


def schedule2json(schedule):
    """serialize schedule into JSON"""
    json_friendly = {}
    json_friendly['annual_periods'] = schedule.annual_periods
    json_friendly['start_date'] = date2json(schedule.start_date)
    json_friendly['end_date'] = date2json(schedule.end_date)
    json_friendly['events'] = []
    for event_date in schedule:
        json_friendly['events'].append(date2json(event_date))
    return json_friendly


def json2schedule(json_schedule):
    """de-serialize schedule from JSON"""
    schedule_events = []
    for event_str in json_schedule['events']:
        parsed = datetime.datetime.strptime(event_str, JSON_DATE_FORMAT)
        schedule_events.append(parsed.date())

    start_date = datetime.datetime.strptime(json_schedule['start_date'],
                                            JSON_DATE_FORMAT)
    end_date = datetime.datetime.strptime(json_schedule['end_date'],
                                          JSON_DATE_FORMAT)
    schedule = CustomSchedule(start_date,
                              end_date,
                              events=schedule_events,
                              annual_periods=json_schedule['annual_periods'],

                              )
    return schedule


if __name__ == '__main__':
    ws = WeeklySchedule(
        start_date=datetime.date(
            2002, 1, 1), end_date=datetime.date(
            2004, 3, 3), weeks=2)
    ms = MonthlySchedule(
        start_date=datetime.date(
            2002, 1, 1), end_date=datetime.date(
            2006, 3, 3), months=2)
    js = schedule2json(ms)
    cs = json2schedule(js)

    pre_set = set(ms)
    post_set = set(cs)

    diff_set = pre_set.difference(post_set)
