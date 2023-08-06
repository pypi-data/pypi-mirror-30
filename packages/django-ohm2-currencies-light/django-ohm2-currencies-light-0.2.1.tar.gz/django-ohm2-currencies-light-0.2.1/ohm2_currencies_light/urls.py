from django.conf.urls import url, include
from . import views

app_name = "ohm2_currencies_light"

urlpatterns = [
	url(r'ohm2_currencies_light/$', views.index, name = 'index'),		
]


