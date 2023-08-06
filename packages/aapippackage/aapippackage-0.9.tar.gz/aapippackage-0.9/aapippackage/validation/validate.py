import datetime
from aapippackage.errors.PromotionError import PromotionError
from aapippackage.errors.NavitaireError import NavitaireException
from aapippackage.errors.StationError import BaseCurrencyNotFound
from aapippackage.errors.ValuePackError import ValuePackError

def dateformat(date_text):
    try:
        datetime.datetime.strptime(date_text, '%Y-%m-%d')
    except ValueError:
        raise ValueError("Incorrect data format, should be YYYY-MM-DD")

def promoCode(promoCode):
    if len(promoCode) > 8:
        raise PromotionError(promoCode + ": but must be no more than 8 characters in length")