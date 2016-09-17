from django.contrib import admin
from django_calendar.models import Eleve, Professeur, Convention, Tuteur, Periode

# Custom model admin
class EleveAdmin(admin.ModelAdmin):
    exclude = ("user",)
    list_display = ("username", "first_name", "last_name", "email", "phone")
    search_fields = ("first_name", "last_name")

class ProfesseurAdmin(admin.ModelAdmin):
    exclude = ("user",)
    list_display = ("username", "first_name", "last_name", "email", "phone")
    search_fields = ("first_name", "last_name")

class TuteurAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "institution", "role", "phone", "email")
    search_fields = ("first_name", "last_name")

class PeriodeInline(admin.TabularInline):
    model = Periode
    readonly_fields = ('start', 'end')
    extra = 0
    def has_add_permission(self, request):
        return False
    can_delete = False
class ConventionAdmin(admin.ModelAdmin):
    list_display = ("stage", "student", "teacher", "tutor", "date_start", "date_end", "periods")
    list_filter = ("stage", "teacher")
    date_hierarchy = ("date_start")
    inlines = (PeriodeInline,)


# Register your models here.
admin.site.register(Eleve, EleveAdmin)
admin.site.register(Professeur, ProfesseurAdmin)
admin.site.register(Tuteur, TuteurAdmin)
admin.site.register(Convention, ConventionAdmin)
# admin.site.register(Periode)
