from django.contrib import admin
from .models import *

admin.site.register(Question)
admin.site.register(UserAnswer)
admin.site.register(Activity)
admin.site.register(Application)
admin.site.register(ApplicationSystemRequirement)
admin.site.register(UserPreference)
