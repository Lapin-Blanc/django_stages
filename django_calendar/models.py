from datetime import date
from datetime import datetime, timedelta
from django.utils import timezone

from django.db import models
from django.contrib.auth.models import User, Group
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_delete
from django.core.exceptions import ValidationError

CHOIX_STAGE = (
    ("OBS","Stage d'observation"),
    ("INS","Stage d'insertion"),
    ("INT","Stage d'intégration"),
)
TYPES_STAGE = {
    ("DOM", "Domiciles"),
    ("MRS", "Maison de repos et de soin"),
    ("MRE", "Maison de repos"),
    ("HOP", "Hôpital"),
}
VENTILATION_STAGE = {
    "OBS" : {"MRE": 65, "MRS" : 65 , "DOM" : 65},
    "INS" : {"MRS" : 100 , "DOM" : 100},
    "INT" : {"MRS" : 70 , "DOM" : 70, "HOP" : 60},
}

# Create your models here.
class Eleve(models.Model):
    username = models.CharField("nom d'utilisateur", max_length=20, unique=True)
    password = models.CharField("mot de passe", max_length=20)
    first_name = models.CharField("prénom", max_length=20)
    last_name = models.CharField("nom", max_length=20)
    email = models.EmailField(blank=True, default="")
    phone = models.CharField("téléphone", max_length=20, blank=True, default="")
    user = models.OneToOneField(User, related_name="eleve", blank=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Éleve"
        verbose_name_plural = "Éleves"

    def __str__(self):
        return "{} {}".format(self.first_name, self.last_name)

    def get_convention(self):
        c = Convention.objects.filter(student=self.id, date_start__lte=datetime.today())
        if len(c) == 0:
            return None
        elif len(c) == 1:
            return c[0]
        else:
            raise Exception("Plus d'une convention planifiée pour cet élève")


class Professeur(models.Model):
    username = models.CharField("nom d'utilisateur", max_length=20, unique=True)
    password = models.CharField("mot de passe", max_length=20)
    first_name = models.CharField("prénom", max_length=20)
    last_name = models.CharField("nom", max_length=20)
    email = models.EmailField(blank=True, default="")
    phone = models.CharField("téléphone", max_length=20, blank=True, default="")
    user = models.OneToOneField(User, related_name="professeur", blank=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Professeur"
        verbose_name_plural = "Professeurs"

    def __str__(self):
        return "%s %s" % (self.first_name, self.last_name,)


@receiver(pre_save, sender=Eleve)
@receiver(pre_save, sender=Professeur)
def pre_save_user(sender, instance, *args, **kwargs):
    # TODO appartenance exclusive professeurs/élèves
    if not instance.pk:
        u = User(
            username=instance.username,
            first_name=instance.first_name,
            last_name=instance.last_name,
            email=instance.email,
            is_staff = (sender == Professeur),
        )
        u.set_password(instance.password)
        u.save()
        if sender == Eleve:
            u.groups.add(Group.objects.get(name="Élèves"))
        else:
            u.groups.add(Group.objects.get(name="Professeurs"))
        instance.user = u
    else:
        u = instance.user
        u.username=instance.username
        u.first_name=instance.first_name
        u.last_name=instance.last_name
        u.email=instance.email
        u.set_password(instance.password)
        u.save()

@receiver(post_delete, sender=Eleve)
@receiver(post_delete, sender=Professeur)
def post_delete_user(sender, instance, *args, **kwargs):
    if instance.user:
        instance.user.delete()

class Lieu(models.Model):
    institution = models.CharField("Institution", max_length=50, unique=True)
    address = models.CharField("rue et numéro", max_length=200, default="")
    zipcode = models.CharField("code postal", max_length=5, blank=True, default="")
    city = models.CharField("localité", max_length=20, blank=True, default="")
    contact = models.CharField("contact", max_length=50, blank=True, default="")
    phone = models.CharField("téléphone", max_length=20, blank=True, default="")


    class Meta:
        verbose_name = "Lieu de stage"
        verbose_name_plural = "Lieux de stage"

    def __str__(self):
        return "%s" % (self.institution,)

class Convention(models.Model):
    place = models.ForeignKey(Lieu, verbose_name="Lieu")
    teacher = models.ForeignKey(Professeur, verbose_name="Professeur")
    student = models.ForeignKey(Eleve, verbose_name="Stagiaire")
    stage = models.CharField(max_length=3, choices = CHOIX_STAGE)
    type_stage = models.CharField(max_length=4, choices = TYPES_STAGE)
    date_start = models.DateField("Date de début")
    date_end = models.DateField("Date de fin", blank=True, null=True)
    periods = models.IntegerField("Nombre de périodes", blank=True, null=True) # planifiée pour cette convention

    def asked_periods(self):
        if self.stage and self.type_stage:
            return VENTILATION_STAGE[self.stage][self.type_stage]
        else:
            return None
    asked_periods.short_description = "Périodes à prester"

    def sum_periods(self):
       return self.periode_set.filter(end__lt=timezone.now()).aggregate(somme=models.Sum('duration'))['somme'] 
#        td = date.today()
#        today_zero = datetime(td.year, td.month, td.day)
#        cnt = self.periode_set.filter(models.Q(end__lt=today_zero)).aggregate(sum=models.Sum("duration"))['sum']
#        if cnt:
#            return cnt
#        else:
#            return 0
    sum_periods.short_description = "Périodes prestées "

    def clean(self):
        if not self.type_stage in VENTILATION_STAGE[self.stage]:
            raise ValidationError({'type_stage' : "Le type de stage (%s) choisit ne convient pas pour le %s" % (\
                                                    dict(TYPES_STAGE)[self.type_stage],
                                                    dict(CHOIX_STAGE)[self.stage].lower(),
                                                    )})
        # print("OK")
        # if self.date_end <= self.date_start:
        #     raise ValidationError("La date de fin doit être après la date de début")
        #
        # this_student_other_conventions = Convention.objects.filter(student=self.student)
        # for c in [other_c for other_c in this_student_other_conventions if other_c.id != self.id ]:
        #     if (self.date_start < c.date_start < self.date_end) or (self.date_start < c.date_end < self.date_end):
        #         raise ValidationError("Une autre convention entre en conflit sur cette période")


    class Meta:
        verbose_name = "Convention"
        verbose_name_plural = "Conventions"

    def __str__(self):
        d_start = self.date_start.strftime("%d/%m/%Y")
        if self.date_end:
            libelle_date = " - du %s au %s" % (d_start, self.date_end.strftime("%d/%m/%Y"),)
        else:
            libelle_date = " à partir du %s" % (d_start,)
        return "%s " % (
            dict(CHOIX_STAGE)[self.stage],
            # self.student.last_name,
            # self.student.first_name,
            ) + libelle_date


class Periode(models.Model):
    convention = models.ForeignKey(Convention, on_delete=models.CASCADE)
    start = models.DateTimeField("Heure de début")
    end = models.DateTimeField("Heure de fin")
    date_created = models.DateTimeField("Date de création", auto_now_add=True)
    date_modified = models.DateTimeField("Date de modification", auto_now=True)
    duration = models.DecimalField("Durée en périodes", max_digits=8, decimal_places=2, default=0)

    def modified(self):
        print("Date création : %s" % (self.date_created))
        print("Date modification : %s" % (self.date_modified))
        if self.date_created and self.date_modified:
            return self.date_created + timedelta(minutes=1) < self.date_modified
        else:
            return False
    modified.boolean = True
    modified.short_description = "A été modifié"

    def clean(self):
        period_date_start = date(self.start.year, self.start.month, self.start.day)
        period_date_end = date(self.end.year, self.end.month, self.end.day)

        if (period_date_start <= date.today()):
            raise ValidationError("Enoodage tardif pour cette plage horaire")

        if (period_date_start < self.convention.date_start):
            raise ValidationError("La plage débute avant le début la convention")

        if self.convention.date_end:
            if (period_date_start > self.convention.date_end):
                raise ValidationError("La plage débute après la find de la convention")
            if (period_date_end > self.convention.date_end):
                raise ValidationError("La plage se termine après la fin de la convention")

        if self.end <= self.start:
            raise ValidationError("La fin de la plage doit être après le début")

        this_convention_other_periods = Periode.objects.filter(convention=self.convention)
        for p in [other_p for other_p in this_convention_other_periods if other_p.id != self.id]:
            if (self.start < p.start <self.end) or (self.start < p.end <self.end):
                raise ValidationError("Les plages horaires ne peuvent se chevaucher")
        self.duration = (self.end - self.start).seconds / (50*60)


    class Meta:
        verbose_name = "Plage horaire"
        verbose_name_plural = "Plages horaires"
        ordering = ("start",)

    def __str__(self):
        return "%s -> %s" % (self.start.strftime("%d/%m/%Y %H:%M"), self.end.strftime("%d/%m/%Y %H:%M"))

#@receiver(pre_save, sender=Convention)
@receiver(pre_save, sender=Periode)
def pre_save_handler(sender, instance, *args, **kwargs):
    instance.clean()
