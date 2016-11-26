from django.contrib import admin
from django_calendar.models import Eleve, Professeur, Convention, Lieu, Periode

# Custom model admin
class EleveAdmin(admin.ModelAdmin):
    exclude = ("user",)
    list_display = ("username", "first_name", "last_name", "email", "phone")
    search_fields = ("first_name", "last_name")

class ProfesseurAdmin(admin.ModelAdmin):
    exclude = ("user",)
    list_display = ("username", "first_name", "last_name", "email", "phone")
    search_fields = ("first_name", "last_name")

class LieuAdmin(admin.ModelAdmin):
    list_display = ("institution", "address", "zipcode", "city", "contact", "phone")
    search_fields = ("institution",)

class PeriodeInline(admin.TabularInline):
    model = Periode
    readonly_fields = ('start', 'end', 'duration', 'date_created', 'date_modified', 'modified')
    extra = 0
    def has_add_permission(self, request):
        return False
    can_delete = False

class ConventionAdmin(admin.ModelAdmin):
    readonly_fields = ('sum_periods', 'asked_periods')
    fields = ("stage", "type_stage", "student", "teacher", "place", "date_start", "date_end", "sum_periods", 'asked_periods')
    list_display = ("stage", "type_stage", "student", "teacher", "place", "date_start", "date_end", "sum_periods", 'asked_periods')
    list_filter = ("stage", "type_stage", "teacher")
    date_hierarchy = ("date_start")
    inlines = [PeriodeInline,]

class PeriodeAdmin(admin.ModelAdmin):
    list_display = ("start", "end", "duration")

# Register your models here.
admin.site.register(Eleve, EleveAdmin)
admin.site.register(Professeur, ProfesseurAdmin)
admin.site.register(Lieu, LieuAdmin)
admin.site.register(Convention, ConventionAdmin)
# admin.site.register(Periode, PeriodeAdmin)
