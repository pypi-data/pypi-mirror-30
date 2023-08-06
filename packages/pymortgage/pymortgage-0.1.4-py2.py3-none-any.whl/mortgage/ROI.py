# coding=UTF-8
from Mortgage import *


class ROI(object):
    """ ATTRIBUTES

    mortgage  (private)
    target_sell_price  (private)
    appreciation  (private)
    baseline_return  (private)
    investments  (private)
    property_tax  (private)
    property_insurance  (private)
    sale expences in % - realtor cut, house reconditioning etc.

    sale_expences  (private)

    end_date  (private)
        end date of investment. Could be mortgage early termination
    """

    def __init__(self,
                 mortgage,
                 target_sell_price,
                 appreciation,
                 baseline_return,
                 investments,
                 property_tax,
                 property_insurance,
                 sale_expences,
                 end_date=None):
        self._mortgage = mortgage
        self._target_sell_price = target_sell_price
        self._appreciation = appreciation
        self._baseline_return = baseline_return
        self._investments = investments
        self._property_tax = property_tax
        self._property_insurance = property_insurance
        self._sale_expences = sale_expences
        self._end_date = end_date
