__author__ = 'marc'
import pandas as pd
from pyTeleTrader import pyTeleTrader

test_url = ""
try:
    stocks = pd.read_csv('/Users/marc/PycharmProjects/KNIPS/PyTeleTrader/test/stocks_tt.csv', sep=';', encoding='latin-1')
except IOError:
    print("IOError ")
    exit(-1)

for index, row in stocks.iterrows():
    test_url = row['TT']
    print(row['TT'])

    # Financials
    tt2 = pyTeleTrader.PyTeleTrader(test_url)
    rc = tt2.get_kpi_history()
    print(rc)

    # Profile
    tt3 = pyTeleTrader.PyTeleTrader(test_url)
    bd = tt3.get_business_description()
    print(bd)

    # Key Statistics
    tt = pyTeleTrader.PyTeleTrader(test_url)
    rc1, rc2 = tt.get_key_statistics()
    print(rc1)
    print(rc2)