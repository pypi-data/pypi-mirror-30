A module to make it easier to handle historical exchange rates.

Currently combines daily rates from the St Louis Federal Reserve with monthly rates from the OECD.

See also <http://thedatahub.org/dataset/exchange-rates>

## Instructions

Install from PyPI:

    pip install exchangerates

Create a CurrencyConverter object:

    import exchangerates
    converter = exchangerates.CurrencyConverter(update=True)

Note: `update=True` will lead to fresh exchange rates being downloaded.

Get a list of the available currencies:

    print converter.known_currencies()

Get the conversion rate for a specific currency and date:

    print converter.closest_rate("USD", datetime.date(2012,7,20))
    print converter.closest_rate("EUR", datetime.date(2014,7,20))
    print converter.closest_rate("EUR", datetime.date(2014,7,20))

You can also just generate a consolidated file of exchange rates:

    python get_rates.py

Result will be at `data/consolidated_rates.csv`.

## Summary of sources

OECD data is monthly, FRED data is daily. FRED data is preferred, but OECD data is used where FRED data is unavailable.

Currency | OECD from | OECD to | FRED from | FRED to
-------- | --------- | ------- | --------- | ----------
AUD | 01/01/1957 | 01/01/1971 | 04/01/1971 | 17/03/2017
BRL | 01/01/1957 | 01/01/1995 | 02/01/1995 | 17/03/2017
CAD | 01/01/1957 | 01/01/1971 | 04/01/1971 | 17/03/2017
CEC | 01/01/1957 | 01/02/2017 |  |
CHF | 01/01/1957 | 01/01/1971 | 04/01/1971 | 17/03/2017
CLP | 01/01/1957 | 01/03/2017 |  |
CNY | 01/01/1957 | 01/01/1981 | 02/01/1981 | 17/03/2017
COP | 01/01/1957 | 01/02/2017 |  |
CZK | 01/01/1991 | 01/03/2017 |  |
DKK | 01/01/1957 | 01/01/1971 | 04/01/1971 | 17/03/2017
EUR | 01/01/1979 | 01/01/1999 | 04/01/1999 | 17/03/2017
GBP | 01/01/1957 | 01/01/1971 | 04/01/1971 | 17/03/2017
HKD |  |  | 02/01/1981 | 17/03/2017
HUF | 01/01/1991 | 01/03/2017 |  |
IDR | 01/01/1967 | 01/01/2017 |  |
ILS | 01/01/1957 | 01/03/2017 |  |
INR | 01/01/1957 | 01/01/1973 | 02/01/1973 | 17/03/2017
ISK | 01/01/1957 | 01/03/2017 |  |
JPY | 01/01/1957 | 01/01/1971 | 04/01/1971 | 17/03/2017
KRW | 01/01/1963 | 01/04/1981 | 13/04/1981 | 17/03/2017
LKR |  |  | 02/01/1973 | 17/03/2017
LVL | 01/02/1992 | 01/03/2017 |  |
MXN | 01/01/1963 | 01/11/1993 | 08/11/1993 | 17/03/2017
MYR |  |  | 04/01/1971 | 17/03/2017
NOK | 01/01/1957 | 01/01/1971 | 04/01/1971 | 17/03/2017
NZD | 01/01/1957 | 01/01/1971 | 04/01/1971 | 17/03/2017
PLN | 01/01/1991 | 01/03/2017 |  |
RUB | 01/06/1992 | 01/02/2017 |  |
SEK | 01/01/1957 | 01/01/1971 | 04/01/1971 | 17/03/2017
SGD |  |  | 02/01/1981 | 17/03/2017
THB |  |  | 02/01/1981 | 17/03/2017
TRY | 01/01/1957 | 01/03/2017 |  |
TWD |  |  | 03/10/1983 | 17/03/2017
VEF |  |  | 02/01/1995 | 17/03/2017
XDR | 01/01/1957 | 01/03/2017 |  |
ZAR | 01/01/1957 | 01/01/1971 | 04/01/1971 | 17/03/2017
