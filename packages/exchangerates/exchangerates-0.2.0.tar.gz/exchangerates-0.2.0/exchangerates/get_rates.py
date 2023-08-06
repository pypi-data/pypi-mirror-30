import csv
import zipfile
import requests
import datetime
import re

from lxml import etree
from six import next, BytesIO

from .util import fred_countries_currencies, oecd_countries_currencies


FRED_RATES = "https://fred.stlouisfed.org/categories/94/downloaddata/INTLFXD_csv_2.zip"
OECD_RATES = "http://stats.oecd.org/restsdmx/sdmx.ashx/GetData/MEI_FIN/CCUS.AUS+AUT+BEL+CAN+CHL+CZE+DNK+EST+FIN+FRA+DEU+GRC+HUN+ISL+IRL+ISR+ITA+JPN+KOR+LVA+LUX+MEX+NLD+NZL+NOR+POL+PRT+SVK+SVN+ESP+SWE+CHE+TUR+GBR+USA+EA19+SDR+NMEC+BRA+CHN+COL+CRI+IND+IDN+RUS+ZAF.M/all?startTime=1950-01"


class ZipExtFileWrapper:
    def __init__(self, zef):
        self.zef = zef

    def __iter__(self):
        while True:
            try:
                yield next(self.zef).decode('utf-8')
            except StopIteration:
                break

    def close(self):
        return self.zef.close()


def get_fred_rates(outfp, writer):
    def extract_file(zfo, id_, from_currency, to_currency, freq):
        fp = 'INTLFXD_csv_2/data/{}'.format(id_)
        fo = ZipExtFileWrapper(zfo.open(fp))
        reader = csv.reader(fo)
        next(reader)
        country = {True: to_currency,
                   False: from_currency}[from_currency == "U.S."]
        for row in reader:
            if row[1] == ".":
                continue
            if from_currency == "U.S.":
                row[1] = round(1/float(row[1]), 4)
            outrow = row + [fred_countries_currencies[country], freq, "FRED"]
            writer.writerow(outrow)
        fo.close()

    def read_files(zfo):
        fo = zfo.open('INTLFXD_csv_2/README_SERIES_ID_SORT.txt')
        for line in fo.readlines():
            line = line.decode('utf-8')
            if not line.startswith("DEX"):
                continue
            columns = line.split(';')
            id_ = columns[0].strip()
            from_currency, to_currency = re.match(
                            "(.*) / (.*) Foreign Exchange Rate", columns[1]
                            ).groups()
            freq = columns[3].strip()
            try:
                extract_file(zfo, id_, from_currency, to_currency, freq)
            except Exception as inst:
                print(id_)
                raise

    r = requests.get(FRED_RATES)
    zfo = zipfile.ZipFile(BytesIO(r.content))
    read_files(zfo)


def get_oecd_rates(outfp, writer):
    def make_date(value):
        return datetime.datetime.strptime(value, "%Y-%m-%d")

    # Find earliest data for each currency from the St Louis Fed data
    def get_earliest_dates():
        outfp_file = open(outfp, "r")
        reader = csv.DictReader(outfp_file)
        indata = list(map(lambda row: row, reader))
        outfp_file.close()

        currencies = dict(map(lambda currency:
                              (currency, None),
                  list(set(map(lambda row: row["Currency"], indata)))))

        for currency in currencies:
            currency_dates = list(map(lambda y:
                      make_date(y["Date"]),
                    filter(lambda x: x['Currency'] == currency, indata)
            ))
            currencies[currency] = min(currency_dates)

        return currencies

    def get_OECD_data(writer, currencies_dates):
        r = requests.get(OECD_RATES)
        fp_doc = etree.fromstring(r.content)
        nsmap = {
            "ns": "http://www.SDMX.org/resources/SDMXML/schemas/v2_0/generic"
        }
        series = fp_doc.findall("ns:DataSet/ns:Series", namespaces=nsmap)
        for serie in series:
            currency = serie.find("ns:SeriesKey/ns:Value[@concept='LOCATION']", namespaces=nsmap).get("value")

            min_currency_date = currencies_dates.get(
                oecd_countries_currencies.get(currency),
                datetime.datetime.utcnow())

            for obs in serie.findall("ns:Obs", namespaces=nsmap):
                date = "{}-01".format(obs.find("ns:Time", namespaces=nsmap).text)
                value = obs.find("ns:ObsValue", namespaces=nsmap).get("value")
                if make_date(date) < min_currency_date:
                    writer.writerow([date, value, oecd_countries_currencies.get(currency), "M", "OECD"])

    currencies_dates = get_earliest_dates()
    get_OECD_data(writer, currencies_dates)


def update_rates(out_filename):
    outfp = out_filename
    outfp_f = open(outfp, 'w')
    writer = csv.writer(outfp_f)
    writer.writerow(['Date', 'Rate', 'Currency', 'Frequency', 'Source'])
    get_fred_rates(outfp, writer)

    writer = csv.writer(outfp_f)
    get_oecd_rates(outfp, writer)
    outfp_f.close()


if __name__ == "__main__":
    update_rates('data/consolidated_rates.csv')
