from django.contrib import admin
from .models import *

for model in admin.site._registry: pass

