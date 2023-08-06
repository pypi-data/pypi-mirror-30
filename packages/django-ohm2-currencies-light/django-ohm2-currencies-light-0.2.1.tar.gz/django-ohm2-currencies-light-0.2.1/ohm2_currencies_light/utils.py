from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.db.models import Q
from ohm2_handlers_light import utils as h_utils
from ohm2_handlers_light.definitions import RunException
from . import models as ohm2_currencies_light_models
from . import errors as ohm2_currencies_light_errors
from . import settings
import os, time, random


random_string = "0K3VdAIdOxbv4QOc1PsforYAC7c58rdA"


def create_currency(alpha_3, name, symbol, decimals, **kwargs):
	kwargs["alpha_3"] = alpha_3.strip()
	kwargs["name"] = name.strip().title()
	kwargs["symbol"] = symbol.strip()
	kwargs["decimals"] = int(decimals)
	return h_utils.db_create(ohm2_currencies_light_models.Currency, **kwargs)

def get_currency(**kwargs):
	return h_utils.db_get(ohm2_currencies_light_models.Currency, **kwargs)

def get_or_none_currency(**kwargs):
	return h_utils.db_get_or_none(ohm2_currencies_light_models.Currency, **kwargs)

def filter_currency(**kwargs):
	return h_utils.db_filter(ohm2_currencies_light_models.Currency, **kwargs)

def delete_currency(entry, **kwargs):
	return h_utils.db_delete(entry)

def create_convertionrate(input, output, source, rate, **kwargs):
	kwargs["input"] = input
	kwargs["output"] = output
	kwargs["source"] = source.strip().title()
	kwargs["rate"] = rate
	return h_utils.db_create(ohm2_currencies_light_models.ConvertionRate, **kwargs)

def get_convertionrate(**kwargs):
	return h_utils.db_get(ohm2_currencies_light_models.ConvertionRate, **kwargs)

def get_or_none_convertionrate(**kwargs):
	return h_utils.db_get_or_none(ohm2_currencies_light_models.ConvertionRate, **kwargs)

def filter_convertionrate(**kwargs):
	return h_utils.db_filter(ohm2_currencies_light_models.ConvertionRate, **kwargs)

def delete_convertionrate(entry, **kwargs):
	return h_utils.db_delete(entry)

def create_lastconvertionrate(input, output, convertion_rate, **kwargs):
	kwargs["input"] = input
	kwargs["output"] = output
	kwargs["convertion_rate"] = convertion_rate
	return h_utils.db_create(ohm2_currencies_light_models.LastConvertionRate, **kwargs)

def get_lastconvertionrate(**kwargs):
	return h_utils.db_get(ohm2_currencies_light_models.LastConvertionRate, **kwargs)

def get_or_none_lastconvertionrate(**kwargs):
	return h_utils.db_get_or_none(ohm2_currencies_light_models.LastConvertionRate, **kwargs)

def filter_lastconvertionrate(**kwargs):
	return h_utils.db_filter(ohm2_currencies_light_models.LastConvertionRate, **kwargs)

def delete_lastconvertionrate(entry, **kwargs):
	return h_utils.db_delete(entry)


