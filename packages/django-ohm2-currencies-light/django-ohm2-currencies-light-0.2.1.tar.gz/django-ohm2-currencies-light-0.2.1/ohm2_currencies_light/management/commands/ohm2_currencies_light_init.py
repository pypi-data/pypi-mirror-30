from django.core.management.base import BaseCommand, CommandError
from ohm2_handlers_light import utils as h_utils
from ohm2_currencies_light import utils as ohm2_currencies_light_utils
import os, pycountry

class Command(BaseCommand):
	
	def add_arguments(self, parser):
		pass #parser.add_argument('-f', '--foo')

	def handle(self, *args, **options):
		# foo = options["foo"]
		CLP = pycountry.currencies.get(alpha_3 = "CLP")
		USD = pycountry.currencies.get(alpha_3 = "USD")
		EUR = pycountry.currencies.get(alpha_3 = "EUR")

		entries = [
			{
				"alpha_3": CLP.alpha_3,
				"name": CLP.name,
				"symbol": "$",
				"decimals": 0,
				"available": True,
			},
			{
				"alpha_3": USD.alpha_3,
				"name": USD.name,
				"symbol": "$",
				"decimals": 2,
				"available": True,
			},
			{
				"alpha_3": EUR.alpha_3,
				"name": EUR.name,
				"symbol": "€",
				"decimals": 2,
				"available": True,
			},
		]

		for e in entries:
			c = ohm2_currencies_light_utils.get_or_none_currency(alpha_3 = e["alpha_3"])
			if c:
				continue
			c = ohm2_currencies_light_utils.create_currency(**e)
			