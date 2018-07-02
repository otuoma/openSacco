import sys
from .mydates import *
from .armot_utils import money
from math import ceil
sys.path.append('')


def get_emi(principal, rate, term, loan_type):
    """"Calculates the EMI on a loan.
    Returns the payment amount on a loan given
    the principal, the interest rate (as an APR),
    and the term (in months)."""

    interest = (rate / 12) / 100

    n = term
    amount = principal

    if loan_type == 'reducing_balance':
        num = ((1 + interest) ** n) - 1
        denm = interest * (1 + interest) ** n
        d = num / denm
        emi = amount / d
    else:  # use flat rate
        total_repayable = (((100 + rate) / 100) * principal)

        emi = total_repayable / term

    return emi


class LoanArmotizer (object):
    """Hold the details of a loan and calculate an amortization schedule.

          originDate     : the date the loan was made
          loanAmount     : the amount loaned (initial principal)
          payment        : the total payment due each month (other than any irregular payments in firstPayments) or "unknown"
          interest       : annual interest rate as a percentage, such as 6 for 6% or 7.25 for 7.25%
          firstPayments  : a list of (date, amount) pairs for initial (possibly) irregular payments
          days           : how many days in a month.  Should be "actual" or "30".  Ignored if period is not "monthly".
          basis          : how many days in a year.  Should be "actual" or "365" or "360".  Ignored if period is not "monthly".
          dueDay         : the day of the month all subsequent payments are due.  If this is
                            not specified, it is the taken as the day of the originDate.
          numberOfPayments : either an integer or "unknown".   Must be known if  payment is "unknown".
          period         : must be "monthly", "quarterly", "semi-annual", or "annual"
          yearsMethod    : must be "civil" or "anniversary"
          # We might later use numberOfPayments="unknown" and payment="unknown" to indicate an interest only loan.
    """
    def __init__(self, originDate, loanAmount, interest, payment="unknown", numberOfPayments="unknown",
                 firstPayments=None, days="actual", basis="actual", dueDay=None, period="monthly", yearsMethod="civil"):
        self.originDate = asDate(originDate)
        self.amount = loanAmount
        self.originalPayment = payment    # so we can remember if payment was "unknown" to begin with
        self.payment = payment
        self.annualRate = interest / 100.0
        self.firstPayments = firstPayments
        self.days = days
        self.basis = basis
        self.dueDay = dueDay
        if self.dueDay is None:
            self.dueDay = self.originDate.day
        self.numberOfPayments = numberOfPayments
        self.period = period
        self.monthsBetweenPayments = {"monthly":1, "quarterly":3, "semi-annual":6, "annual":12}[self.period]
        self.paymentsPerYear = {"monthly":12, "quarterly":4, "semi-annual":2, "annual":1}[self.period]
        self.yearsMethod = yearsMethod

        self.principal = float(self.amount)
        self.lastPayment = originDate  # a slight misnomer at first
        self.payments = None

        fractionChoices = {"monthly": "", "quarterly": "quarter year", "semi-annual": "half year", "annual": "full year"}
        self.fraction = fractionChoices[self.period]

        if type (payment) is int:
            self.payment = float(payment)

        if not (payment == "unknown" or type(payment) is float):
            raise ValueError('payment must be either "unknown" or an integer (such as 100) or a float (such as 100.00)')

        if not ((numberOfPayments == "unknown") or type(numberOfPayments) is int):
            raise ValueError('numberOfPayments must be either "unknown" or an integer (such as 20 or 36")')

        if (payment == "unknown") and (numberOfPayments == "unknown"):
            raise ValueError('payment and numberOfPayments cannot both be "unknown"')

        if payment == "unknown":
            """Calculate the payment based upon period, interest rate, and number
               of payments.
            """
            self.payment = self.calculatePayment()

        if not (type(self.days) is str):
           raise ValueError ('days must be in quotation marks')
        if not (self.days in ["actual", "30"]):
           raise ValueError ('days must be either "actual" or "30"')

        if not (type(self.basis) is str):
           raise ValueError ('basis must be in quotation marks')
        if not (self.basis in ["actual", "365", "360"]):
           raise ValueError ('basis must be either "actual" or "365" or "360"')

        self.schedule = []
        self.lastNewPrincipal = 0.00

    def nextPayment (self):
        # This is a generator function and returns a generator.
        # Call it like this:
        #     np = nextPayment()
        #     while <whatever>:
        #        next(np)
        yield (self.originDate, 0.00)
        lastDate = self.originDate
        if self.firstPayments:
            for dt,amt in self.firstPayments:
                yield (asDate(dt),amt)
                lastDate = asDate(dt)
        cnt = 0
        # while True and (cnt < 100):     # for testing
        while True:
            # What we want to do is find the month that follows the last date,
            #  and then plug the  dueDay and the proper year into it.
            cnt += 1

            newDate = addMonths(lastDate, self.monthsBetweenPayments)
            (y, m, d) = tupleFromDate(newDate)
            newDate = dateFromTuple((y, m, self.dueDay))
            lastDate = newDate
            yield (newDate, self.payment)
            if (self.numberOfPayments == "unknown") and (cnt > (12 * 35)):
                # If we haven't finished after 35 years of monthly
                # payments (or even more years of quarterly etc.), then
                # probably the wrong payment amount has been entered.
                raise ValueError ('Balance not declining due to too small a payment?')

    def calculateSchedule (self):
        """ Create a list of payments where each item contains principal,
            date, payment amount, interest, new principal.  Terminate
            when the principal is zero or the numberOfPayments has been
            reached.
        """

        np = self.nextPayment()
        items = []
        prevDt, _ = next(np)
        principal = self.amount

        paymentNumber = 1
        newPrincipal = 0
        while (principal > 0.00) and ((self.numberOfPayments == "unknown") or (paymentNumber <= self.numberOfPayments)):
            (dt, pmt) = next(np)

            fraction,interest = self.calculateInterest(prevDt,dt,principal)
            newAmountOwed = principal + interest
            pmt = min(pmt, newAmountOwed)
            towardPrincipal = max((pmt - interest), 0.00)
            newPrincipal = round(newAmountOwed - pmt, 2)
            newItem = [paymentNumber, dt, principal, pmt, fraction, interest, towardPrincipal, newPrincipal]
            items.append(newItem)
            principal = newPrincipal
            prevDt = dt
            paymentNumber += 1

        self.schedule = items
        self.lastNewPrincipal = newPrincipal
        # self.lastNewPrincipal = self.lastNewPrincipal

        return self.lastNewPrincipal

    def printSchedule (self):
        items = self.schedule

        items_list = []

        for i in items:
            num, dt, prev, pmt, fraction, interest, towardPrincipal, newPrincipal = i
            # formattedItems = (num, stringFromDate(dt), money(prev, 12), money(pmt, 12), fraction, money(interest, 8), money(towardPrincipal, 10), money(newPrincipal, 12))
            obj = {
                'num': num,
                'date': stringFromDate(dt),
                'prev_balance': money(prev, 12),
                'emi': money(pmt, 12),
                'interest': money(interest, 8),
                'principal': money(towardPrincipal, 10),
                'balance': money(newPrincipal, 12),
            }
            # print(" %4d  %10s  %12s   %12s   %-13s  %12s  %12s  %12s" % formattedItems)
            items_list.append(obj)

        return items_list

    def amort (self):
        finished = False
        while not finished:
            #print ("Calculate schedule with payment of %-.2f" % self.payment)
            self.calculateSchedule()
            if (self.originalPayment == "unknown") and (self.lastNewPrincipal > 0.00):
                self.payment += 0.01  # bump it by a penny and try again
            else:
                finished = True
            if self.lastNewPrincipal > 0.00:
                # We have a balloon payment, so add what would have
                #  been the last new principal to the last payment,
                #  thus wiping out the last new principal.
                self.schedule[-1][3] += self.lastNewPrincipal   # bump payment
                self.schedule[-1][6] += self.lastNewPrincipal   # pump towardPrincipal
                self.schedule[-1][-1] = 0.00

        return self.printSchedule()

    def daysElapsed (self, prev, cur):
        """ Calculate the number of days this period to use for determining
            the interest for this period.  This depends on whether we
            use actual or 30.
        """
        actualDays = daysBetween (prev, cur)
        if self.days == "actual":
            return actualDays
        elif self.days == "30":
            return min(actualDays, 30)
            # FIXME: I'm not sure the elif above is exactly right?  For
            # example, might we have 30/actual where we have to split a
            # payment in January across two years?  Or, what if there
            # are irregular payments?
        else:
            raise RuntimeError("Unexpected else condition in daysElapsed()")

    def daysInYear (self, cur):
        """ Calculate the number of days in the year for the basis of the
            interest calculation.  This is actual or 365 or 360.  In
            the case of "actual", we consider leap year.  There are
            two common ways: (1) civil year or (2) anniversary.
        """

        if self.yearsMethod == "civil":
           # Civil year method:

           #  cur represents the ending date of an interest period.
           #   E.g., for the period Dec 12, 2014 to Jan 12, 2015, cur
           #   would be Jan 12, 2015.  We want to know if the day
           #   before (i.e., Jan 11, 2015) falls in a leap year.  The
           #   tricky case is Dec x,YYYY to Jan 1, YYYY+1.  The day
           #   before is Dec 31, YYYY, and that's the date that
           #   matters for whether this period has 366 or 365 days.
           #   (Because the interest includes the "from" date but not
           #   the "to" date.)

            if isLeapYear(yesterday(cur)):
                return 366
            else:
                return 365
        else:
            # Anniversary method
            # In this case, we do not back cur up by a day, as the daysBetween
            # takes care of that for us.

            aYearAgo = subtractOneYear(cur)
            return daysBetween(aYearAgo, cur)

    def calculateInterest (self, prevDate, curDate, principal):
        """Answer a (fraction,interest) tuple where fraction is a string
           representing the portion of the year over which the
           interest is calculated.

           In the case of monthly actual/actual, a period spanning
           January 1st would look something like "20/365,11/366".
           Otherwise, for monthly, it would look like "31/365".  For
           other periods, it would be "quarter year", "half year", or
           "full year".

           When period is not monthly, interest does not consider the
           actual number of days, just the fraction of the year.

        """
        if self.period == "monthly":
            if (self.days == "actual") and (prevDate.year != curDate.year) and ((curDate.month > 2) or (curDate.day > 1)):
                # Do we cross the end of the year?  That is are some
                # of the days in one year and some in the following
                # year?  Note, Dec x to Jan 1 does not cross, but Dec
                # x to Jan 2 or later does.  Thus, we must compute the
                # interest in two steps (one for the days in each of
                # the two years).
                jan1st = dateFromTuple((curDate.year, 1, 1)) # Jan 1st of curDate.year
                ndays1 = self.daysElapsed(prevDate, jan1st)
                ydays1 = self.daysInYear(jan1st)

                ndays2 = self.daysElapsed (jan1st, curDate)  # days from Jan 1st to curDate
                ydays2 = self.daysInYear (curDate)
                fraction = "%s/%s,%s/%s" % (ndays1, ydays1, ndays2, ydays2)
                int1 = (principal * ndays1 * self.annualRate) / ydays1
                int2 = (principal * ndays2 * self.annualRate) / ydays2
                interest = round(int1 + int2, 2)
            else:
                # We do not need to split the days into to parts (even
                # if we cross a year boundary).
                ndays = self.daysElapsed(prevDate, curDate)
                ydays = self.daysInYear(curDate)
                fraction = "%s/%s" % (ndays, ydays)
                interest = round((principal * ndays * self.annualRate) / ydays, 2)
        else:
            # since it is not monthly, it must be "quarterly", "semi-annual", or "annual"
            fraction = self.fraction
            interest = principal * self.annualRate
            if self.period == "quarterly":
                interest = interest / 4.0
            elif self.period == "semi-annual":
                interest = interest / 2.0
            elif self.period == "annual":
                pass  # i.e., divide by 1.0

        return fraction, interest

    def calculatePayment(self):
        """Calculate the periodic payment from the initial loanAmount, the
           annual interest rate, and the number of payments total and
           per year. Answer the monthly payment.
        """
        return calculatePayment(self.amount, self.numberOfPayments, self.annualRate, self.paymentsPerYear)

def calculatePayment(loanAmount, nPayments, annualRate, nPaymentsPerYear=12):
    """Calculate the periodic payment from the initial loanAmount, the
       annual interest rate, and the number of payments total and
       per year. Answer the monthly payment. E.g., $1000.00 at 7% repaid monthly over 15 payments:

           calculatePayment (1000.00, 15, 0.07, 12)

    """
    pv = loanAmount
    r = annualRate / nPaymentsPerYear
    n = nPayments
    numerator = r * pv
    denominator = 1 - pow(1 + r, -n)
    pmt = numerator / denominator
    # print ("(pv,r,n,numerator,denominator,pmt) = (%s,%s,%s,%s,%s,%s)" % (pv, r, n, numerator, denominator, pmt))
    # print ("100 * pmt = %s" % (100 * pmt))
    # print ("ceil(100 * pmt) = %s" % (ceil(100 * pmt)))
    # print ("round (ceil(100 * pmt) / 100, 2) = %s" % (round (ceil(100 * pmt) / 100, 2)))
    return round(ceil(100 * pmt) / 100, 2)


if __name__ == '__main__':

    # When called directly, do an example amortization

    loan1 = LoanArmotizer(
        # In the following,
        #   the loan is made on March 10, 2014 in the amount of $2,000.00, with a monthly payment due of $100.00,
        #   the interest rate is 7% per annum, two first payments are specified, interest will be calculated
        #   on an actual/actual basis, and the due date (after any first payments) will be the 10th of the month.
        originDate="2014-03-10",
        loanAmount=2000.00,
        payment="100.00",
        interest=7,
        firstPayments=(("2014-04-15", 100.00),
                       ("2014-05-10", 100.00)),
        days="actual",
        basis="actual",
        dueDay=10,
        numberOfPayments="unknown")

    loan1.amort()
