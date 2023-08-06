from bisect import bisect_left
import csv
import datetime
import pkg_resources

from six import next

from . import get_rates


class UnknownCurrencyException(Exception):
    pass


def make_date_from_iso(iso_str):
    year = int(iso_str[:4])
    month = int(iso_str[5:7])
    day = int(iso_str[8:10])
    return datetime.date(year, month, day)


def take_closest(myList, myNumber):
    # Source: http://stackoverflow.com/a/12141511
    """
    Assumes myList is sorted. Returns closest value to myNumber.
    If two numbers are equally close, return the smallest number.
    """
    pos = bisect_left(myList, myNumber)
    if pos == 0:
        return myList[0]
    if pos == len(myList):
        return myList[-1]
    before = myList[pos - 1]
    after = myList[pos]
    if after - myNumber < myNumber - before:
        return after
    else:
        return before


class CurrencyConverter(object):
    def __init__(self, update=False, source=False):
        def load_rates():
            """
            Read CSV file as generator function
            """
            if self.source is False:
                resource_package = __name__
                resource_path = 'consolidated_rates.csv'
                source = pkg_resources.resource_filename(
                    resource_package, resource_path)

            if update is True:
                get_rates.update_rates(source)
            with open(source, "rU") as data:
                csv_reader = csv.reader(data)
                next(csv_reader)
                for row in csv_reader:
                    yield row

        def make_rates(rates_list):
            """
            Sort rates into nice dictionary of currency: dates
            """
            def append_path(root, paths):
                root.setdefault(paths[0], {})
                root[paths[0]].update(paths[1])
                return root

            rates_dates = {}
            for row in rates_list:
                rates_dates = append_path(
                    rates_dates,
                    (row[2], {make_date_from_iso(row[0]): float(row[1])}))
            currencies_dates = dict(map(lambda currency:
                            (currency, sorted(list(rates_dates[currency]))),
                            rates_dates.keys()))
            return currencies_dates, rates_dates

        self.source = source
        self.currencies_dates, self.dates_rates = make_rates(load_rates())

    def known_currencies(self):
        return ",".join(sorted(self.currencies_dates.keys()))

    def closest_rate(self, currency, date):
        """
        Accepts a list with (currency, date)
        returns currency, date, conversion date, exchange rate
        """
        if currency == u"USD":
            return {"closest_date": date, "conversion_rate": 1.0}
        try:
            the_date = take_closest(self.currencies_dates[currency], date)
            return {
                "closest_date": the_date,
                "conversion_rate": self.dates_rates[currency][the_date]
            }
        except KeyError:
            msg = "Unknown currency: {}".format(currency)
            raise UnknownCurrencyException(msg)


if __name__ == "__main__":
    """
    Example output
    """
    converter = CurrencyConverter(update=True)
    print("Available currencies: {}".format(converter.known_currencies()))
    print(converter.closest_rate("USD", datetime.date(2012, 7, 20)))
    print(converter.closest_rate("EUR", datetime.date(2014, 7, 20)))
    print(converter.closest_rate("EUR", datetime.date(2014, 7, 20)))
