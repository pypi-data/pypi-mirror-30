from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from django.utils.translation import ugettext as _
from ohm2_handlers_light.models import BaseModel
from . import managers
from . import settings
import pycountry



class Currency(BaseModel):
	alpha_3_choices = sorted( tuple( [ (c.alpha_3, c.name) for c in list(pycountry.currencies)] ), key = lambda tup: tup[1] )
	
	alpha_3 = models.CharField(max_length = settings.STRING_SHORT, choices = alpha_3_choices, unique = True)
	name = models.CharField(max_length = settings.STRING_NORMAL)
	symbol = models.CharField(max_length = settings.STRING_SHORT)
	decimals = models.PositiveIntegerField()
	available = models.BooleanField(default = True)
		
	def __str__(self):
		return "[%s] %s" % (self.alpha_3, self.name)


class ConvertionRate(BaseModel):
	input = models.ForeignKey(Currency, on_delete = models.CASCADE, related_name = 'cr_input_currency')
	output = models.ForeignKey(Currency, on_delete = models.CASCADE, related_name = 'cr_output_currency')
	source = models.CharField(max_length = settings.STRING_NORMAL)
	rate = models.FloatField()
	

class LastConvertionRate(BaseModel):
	input = models.ForeignKey(Currency, on_delete = models.CASCADE, related_name = 'lcr_input_currency')
	output = models.ForeignKey(Currency, on_delete = models.CASCADE, related_name = 'lcr_output_currency')
	convertion_rate = models.OneToOneField(ConvertionRate, on_delete = models.CASCADE)

	