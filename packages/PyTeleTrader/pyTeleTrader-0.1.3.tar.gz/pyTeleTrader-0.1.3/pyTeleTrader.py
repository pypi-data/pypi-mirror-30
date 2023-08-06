__author__ = 'marc beder'
import sys
import logging
import requests
from bs4 import BeautifulSoup
from pandas import DataFrame
import numpy as np

FINANCIALS = {'Earnings per Share', 'Revenues', 'Operating Result', 'Income Before Taxes', 'Employees', 'Dividend per Share',
              'Net Income'}

KEY_STATISTICS = {'Earnings per Share:', 'EPS Diluted:','Revenues per Share:', 'Book Value per Share:','Cash Flow per Share:', 'Dividend per Share:',
                  'Revenues:', 'Net Income:', 'Operating Cash Flow:', 'Cash and Cash Equivalents:',
                  'P/E Ratio:', 'P/S Ratio:', 'P/BV ratio:', 'P/CF Ratio:', 'PEG:', 'Earnings Yield:', 'Dividend Yield:',
                  'Market Capitalization:', 'Free Float Market Cap.:', 'Market Cap. / Employee:', 'Shares Outstanding:',
                  'Gross Profit Margin:', 'EBIT Margin:', 'Net Profit Margin:', 'Return on Equity:', 'Return on Assets:',
                  'Liquidity I / Cash Ratio:', 'Liquidity II / Quick Ratio:', 'Liquidity III / Current Ratio:', 'Debt / Equity Ratio:', 'Dynam. Debt / Equity Ratio:',
                  'Employees:', 'Personal Expenses / Employee:', 'Revenues / Employee:', 'Net Income / Employee:', 'Total Assets / Employee:'}


class PyTeleTrader():
    """
    A class to scrape Teletrader information 
    
    Examples:
        test_url = "http://www.teletrader.com/fuchs-petrol-se-vzo-o-n/stocks/details/tts-458949"

    # Financials
    tt2 = TeleTrader(test_url)
    rc = tt2.get_kpi_history()
    print(rc)

    # Profile
    tt3 = TeleTrader(test_url)
    bd = tt3.get_business_description()
    print(bd)

    # Key Statistics
    tt = TeleTrader(test_url)
    rc1, rc2 = tt.get_key_statistics()
    print(rc1)
    print(rc2)    
    """

    def __init__(self, url1):

        logging.basicConfig(stream=sys.stderr, level=logging.WARN)
        self.url_fig = ""
        self.url_bs = ""
        self.url_prf = ""
        self.key_statistics1 = {}
        self.key_statistics2 = {}
        self.tt_start_year = 2012

        if url1.find("details") != -1:
            url_fig = url1.replace("details", "figures")
            url_bs = url1.replace("details", "balancesheet")
            url_prf = url1.replace("details", "profile")
        else:
            exit()

        self.url_fig = url_fig
        self.url_bs = url_bs
        self.url_prf = url_prf

        # Load profile
        self.page_prf = requests.get(self.url_prf)
        self.soup_prf = BeautifulSoup(self.page_prf.content, 'html.parser')

        # Load figures
        self.page_fig = requests.get(self.url_fig)
        self.soup_fig = BeautifulSoup(self.page_fig.content, 'html.parser')

        # Load balancesheet
        self.page_bs = requests.get(self.url_bs)
        self.soup_bs = BeautifulSoup(self.page_bs.content, 'html.parser')

        # Dataframe for results
        columns = FINANCIALS
        self.df = DataFrame(columns=columns)

    def get_key_statistics(self):

        for kpi in KEY_STATISTICS:
            try:
                self.tr_types = self.soup_fig.findAll("tr", {"class": {"even", "odd"}})
                desc = self.soup_fig.find("td", text=kpi).text
                val = self.soup_fig.find("td", text=kpi).find_next_sibling("td").text
                val2 = self.soup_fig.find("td", text=kpi).find_next_sibling("td").find_next_sibling("td")
                val2 = BeautifulSoup(str(val2), 'html.parser').text
                #print(str(desc) + '\t' + str(val) + '\t' + str(val2))
                self.key_statistics1[str(desc)] = str(val)
                self.key_statistics2[str(desc)] = str(val2)
            except AttributeError:
                logging.debug("Tag nicht gefunden.")

        return (self.key_statistics1, self.key_statistics2)


    def get_kpi_history(self):

        for kpi in FINANCIALS:
            self.tr_types = self.soup_bs.findAll("tr", {"class": {"even", "odd"}})
            for tr_type in self.tr_types:
                kpis = tr_type.text.find(kpi)
                if kpis > -1:
                    val = tr_type.findAll('td')
                    val1 = BeautifulSoup(str(val), 'html.parser')
                    val2 = val1.findAll('td')
                    for i in range(0, 5):
                        try:
                            self.df.loc[i + self.tt_start_year, kpi] = val2[i*2+3].text
                        except ValueError:
                            self.df.loc[i + self.tt_start_year, kpi] = np.NaN
                        except IndexError:
                            self.df.loc[i + self.tt_start_year, kpi] = np.NaN
        return self.df

    def get_page_figures(self):
        return self.page_fig.content


    def get_business_description(self):
        self.bd = self.soup_prf.findAll("div", {"class": "component textblock"})
        text = BeautifulSoup(str(self.bd), "html.parser").text
        text = text.replace("[","")
        text = text.replace("]", "")
        #print(text)
        return text


if __name__ == "__main__":

    test_url = "http://www.teletrader.com/daimler-ag-na-o-n/stocks/details/tts-459135"   # Daimler

    # Financials
    tt2 = PyTeleTrader(test_url)
    rc = tt2.get_kpi_history()
    print(rc)

    # Profile
    tt3 = PyTeleTrader(test_url)
    bd = tt3.get_business_description()
    print(bd)

    # Key Statistics
    tt = PyTeleTrader(test_url)
    rc1, rc2 = tt.get_key_statistics()
    print(rc1)
    print(rc2)
