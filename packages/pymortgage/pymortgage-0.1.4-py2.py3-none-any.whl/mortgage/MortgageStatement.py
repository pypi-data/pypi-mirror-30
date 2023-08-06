#!/bin/env python

from TermScheduler import date2json, json2date
from decimal import Decimal


class MortgageStatement(object):
    _principal = None
    _interest = None
    _principal_left = None
    _remaining_balance = None
    _date = None
    _period = None

    def __init__(self, principal, interest, period, payment_date, remaining_balance):
        self._principal = principal
        self._interest = interest
        self._period = period
        self._remaining_balance = remaining_balance
        self._date = payment_date

    @property
    def remaining_balance(self):
        return self._remaining_balance

    @property
    def period(self):
        return self._period

    def get_principal(self):
        return self._principal

    def set_principal(self, principal):
        self._principal = principal

    principal = property(fget=get_principal, fset=set_principal)

    def get_interest(self):
        return self._interest

    def set_interest(self, interest):
        self._interest = interest

    interest = property(fget=get_interest, fset=set_interest)

    def get_principal_left(self):
        return self._principal_left

    def set_principal_left(self, principal):
        self._principal = principal

    principal_left = property(fget=get_principal_left, fset=set_principal_left)

    @property
    def contribution(self):
        """monthly contribution"""
        return self.principal + self.interest

    def __str__(self):
        return "{0:>3} {1:>10} principal:{2:.2f} interest:{3:.2f} remaining:{4:.2f}".format(
            self.period, str(self._date), self.principal, self.interest,
            self.remaining_balance)

    def serialize_json(self):
        return {'period': self.period,
                'date': date2json(self._date),
                'principal': str(self.principal),
                'interest': str(self.interest),
                'remaining_balance': str(self.remaining_balance)}

    def deserialize_json(self, data):
        self.period = data['period']
        self._date = json2date(data['date'])
        self.principal = Decimal(data['principal'])
        self.interest = Decimal(data['interest'])
        self.remaining_balance = Decimal(data['remaining_balance'])
