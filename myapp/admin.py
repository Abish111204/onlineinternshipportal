from django.contrib import admin
from .models import Register, Employer, Internship, Applications

# Register your models so they show up in the admin panel
admin.site.register(Register)
admin.site.register(Employer)
admin.site.register(Internship)
admin.site.register(Applications)