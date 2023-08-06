#!/bin/env python


class MonthlyROI(object):

    _year = None
    _month = None
    _mortgage_payment = None
    _principal_paid = None
    _interest_paid = None
    _appreciated_price = None
    _tax = None
    _insurance = None
    _writeoff = None
    _net_worth_gain = None
    _appreciated_net_worth_gain = None
    _rent_equivalent = None
    _apppreciated_rent_equivalent = None
    _mortgage = None

    def __init__(self, year, month,
                 mortgage_payment, principal_paid,
                 interest_paid, appreciated_price,
                 tax, insurance, writeoff, net_worth_gain,
                 appreciated_net_worth_gain, rent_equivalent,
                 appreciated_rent_equivalent, mortgage):
        self._year = year
        self._month = month
        self._mortgage_payment = mortgage_payment
        self._principal_paid = principal_paid
        self._interest_paid = interest_paid
        self._appreciated_price = appreciated_price
        self._tax = tax
        self._insurance = insurance
        self._writeoff = writeoff
        self._net_worth_gain = net_worth_gain
        self._appreciated_net_worth_gain = appreciated_net_worth_gain
        self._rent_equivalent = rent_equivalent
        self._apppreciated_rent_equivalent = appreciated_rent_equivalent
        self._mortgage = mortgage

    def _str_(self):
        """
        @return string :
        @author
        """
        pass

    def header(self):
        """
        @return string :
        @author
        """
        pass
