from django.contrib import admin
from django_calendar.models import Eleve, Professeur, Convention, Tuteur, Periode
# Register your models here.
admin.site.register(Eleve)
admin.site.register(Professeur)
admin.site.register(Convention)
admin.site.register(Tuteur)
admin.site.register(Periode)
