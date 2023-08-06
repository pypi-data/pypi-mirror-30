# coding=UTF-8

import decimal
from UserDict import UserDict
from MortgageStatement import MortgageStatement

DOLLAR_QUANTIZE = decimal.Decimal('.01')


def dollar(f, round=decimal.ROUND_CEILING):
    """
    This function rounds the passed float to 2 decimal places.
    """
    if not isinstance(f, decimal.Decimal):
        f = decimal.Decimal(str(f))
    return f.quantize(DOLLAR_QUANTIZE, rounding=round)


class Mortgage(object):

    _term = None   # payment_per_year * years
    _house_price = None
    _downpayment = None
    _interest = None
    _start_date = None
    _annual_payment_periods = None

    def __init__(self, house_price, interest, downpayment, schedule):
        """
        @param decimal house_price
        @param int term
        @param decimal interest
        @param decimal downplayment
        @param TermSchedule schedule
        @param int payment_periods
        """
        # self._term = term
        self._house_price = house_price
        self._downpayment = downpayment
        self._interest = interest
        # self._start_date = schedule
        # self._annual_payment_periods = annual_payment_periods

        self._annual_payment_periods = schedule.annual_periods
        self._schedule = list(schedule)
        self._term = len(self._schedule)
        # print("Annual payment periods: {0}\nSchedule: {1}\nTerm: {2}".format(self._annual_payment_periods, str(self._schedule), self._term))

    def period_prepayment(self, period):
        """
         abstract function/hook for prepayment organization

        @param int period :
        @return float :
        @author
        """
        return 0
        # raise NotImplemented

    @property
    def period_growth(self):
        return 1. + self._interest / self._annual_payment_periods

    @property
    def loan_periods(self):
        return self._term

    @property
    def period_payment(self):
        """ Periodic payment sum:
            how much is the payment per period"""
        # https://www.wikihow.com/Calculate-Mortgage-Payments
        p_interest = self.interest / self._annual_payment_periods
        pre_amt = self.principal * (p_interest * (1 + p_interest) **
                                    self.loan_periods) / ((1 + p_interest)**self.loan_periods - 1)
        return dollar(pre_amt, round=decimal.ROUND_CEILING)

    @property
    def schedule(self):
        return self._schedule

    @property
    def interest(self):
        return self._interest

    @property
    def principal(self):
        """ Principal borrowed """
        return self._house_price - self._downpayment

    def payments(self):
        """
         iterator function

        @return MontlyMortgage :
        @author
        """
        current_balance = dollar(self.principal)
        interest_decimal = decimal.Decimal(str(self.interest)).quantize(decimal.Decimal('.000001'))
        for payment_period, payment_date in enumerate(self._schedule, 1):
            interest_unrounded = current_balance * interest_decimal * \
                decimal.Decimal(1) / self._annual_payment_periods
            paid_interest = dollar(interest_unrounded, round=decimal.ROUND_HALF_UP)
            full_payment = self.period_payment + self.period_prepayment(payment_period)
            paid_principal = full_payment - paid_interest
            if full_payment >= current_balance + paid_interest:
                yield MortgageStatement(current_balance, paid_interest, payment_period, payment_date, 0)
                # yield balance, interest
                break
            current_balance -= paid_principal
            yield MortgageStatement(paid_principal, paid_interest, payment_period, payment_date, current_balance)


class RapidPayMortgage(Mortgage):
    """Normal mortgage with additional principal payments each pay period"""

    def __init__(self, house_price, interest, downpayment, schedule, prepayment_schedule):
        super(RapidPayMortgage, self).__init__(house_price, interest, downpayment, schedule)
        self._prepayment_schedule = prepayment_schedule

    def period_prepayment(self, period):
        return self._prepayment_schedule[period]


class PrePrepaymentSchedule(UserDict):
    def __init__(self, payment_schedule):
        self._payment_schedule = list(payment_schedule)
        self.data = {}
        # self._prepayment_schedule={}

    def addPayment(self, payment_period, payment):
        if payment_period not in self.data:
            self.data[payment_period] = payment
        else:
            self.data[payment_period] += payment

    def addPaymentOnDate(self, payment_date, payment):
        for payment_period, p in enumerate(self._payment_schedule, 1):
            if p > payment_date:
                self.addPayment(payment_period, payment)
                break
        else:
            if p <= payment_date:
                self.add(payment_period, payment)

    def __str__(self):
        return str(self.data)

    def __setitem__(self, period, payment):
        """set payment for specified period"""
        self.addPayment(period, payment)

    def __getitem__(self, period):
        if period in self.data:
            return self.data[period]
        else:
            return 0


if __name__ == '__main__':
    from datetime import date
    from TermScheduler import monthly_schedule
    # m = Mortgage(300000, 0.035, 300000 * 0.2, monthly_schedule(date(2009,10,1),30))
    m = Mortgage(300000, 0.035, 300000 * 0.2, monthly_schedule(date(2009, 10, 1), 15))

    principal, interest = 0, 0

    for p in m.payments():
        principal += p.principal
        interest += p.interest
        print(p)

    print("Total paid {0:.2f} principal and {1:.2f} interest".format(principal, interest))

    ms = monthly_schedule(date(2009, 10, 1), 15)
    pps = PrePrepaymentSchedule(ms)
    print(str(pps))
    pps[14] = 1000
    pps[174] = 1000
    print(str(pps))
    pps.addPaymentOnDate(date(2024, 7, 5), 2000)
    print(str(pps))
    print(str(pps[175]))

    # since we've got to restart iterator... need a new instance of the same:
    ms = monthly_schedule(date(2009, 10, 1), 15)
    m = RapidPayMortgage(300000, 0.035, 300000 * 0.2, ms, pps)
    principal, interest = 0, 0

    for p in m.payments():
        principal += p.principal
        interest += p.interest
        print(p)

    print("Total paid {0:.2f} principal and {1:.2f} interest".format(principal, interest))
