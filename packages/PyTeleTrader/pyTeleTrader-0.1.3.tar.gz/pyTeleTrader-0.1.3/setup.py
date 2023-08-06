from distutils.core import setup

setup(
    name='pyTeleTrader',
    version='0.1.3',
    author='Marc Beder',
    author_email='marcbeder@yahoo.de',
    py_modules = ['pyTeleTrader'],
    url='http://pypi.python.org/pypi/pyTeleTrader/',
    license='LICENSE.txt',
    description='Extraction tool for stock info from www.teletrader.com site.',
    long_description=open('README.txt').read(),
    scripts=[
        'test/stocks_tt.csv',
        'test/test_tt.py',
        ]
)


