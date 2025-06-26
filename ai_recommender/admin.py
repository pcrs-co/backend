from django.contrib import admin
from .models import *

admin.site.register(Activity)
admin.site.register(Application)
admin.site.register(ApplicationSystemRequirement)
admin.site.register(UserPreference)
admin.site.register(CPUBenchmark)
admin.site.register(DiskBenchmark)
admin.site.register(GPUBenchmark)
