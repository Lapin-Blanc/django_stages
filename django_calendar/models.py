from datetime import date

from django.db import models
from django.contrib.auth.models import User, Group
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_delete
from django.core.exceptions import ValidationError

CHOIX_STAGE = (
    ("Stage d'observation","Stage d'observation"),
    ("Stage d'insertion","Stage d'insertion"),
    ("Stage d'intégration","Stage d'intégration"),
)
# Create your models here.
class Eleve(models.Model):
    username = models.CharField("nom d'utilisateur", max_length=20)
    password = models.CharField("mot de passe", max_length=20)
    first_name = models.CharField("prénom", max_length=20, blank=True, default="")
    last_name = models.CharField("nom", max_length=20, blank=True, default="")
    email = models.EmailField(blank=True, default="")
    phone = models.CharField("téléphone", max_length=20, blank=True, default="")
    user = models.OneToOneField(User, related_name="eleve_user", blank=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Éleve"
        verbose_name_plural = "Éleves"

    def __str__(self):
        return self.username


class Professeur(models.Model):
    username = models.CharField("nom d'utilisateur", max_length=20)
    password = models.CharField("mot de passe", max_length=20)
    first_name = models.CharField("prénom", max_length=20, blank=True, default="")
    last_name = models.CharField("nom", max_length=20, blank=True, default="")
    email = models.EmailField(blank=True, default="")
    phone = models.CharField("téléphone", max_length=20, blank=True, default="")
    user = models.OneToOneField(User, related_name="professeur_user", blank=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name = "Professeur"
        verbose_name_plural = "Professeurs"

    def __str__(self):
        return self.username


@receiver(pre_save, sender=Eleve)
@receiver(pre_save, sender=Professeur)
def pre_save_user(sender, instance, *args, **kwargs):
    if not instance.pk:
        u = User(
            username=instance.username,
            first_name=instance.first_name,
            last_name=instance.last_name,
            email=instance.email
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

class Tuteur(models.Model):
    first_name = models.CharField("prénom", max_length=20, default="")
    last_name = models.CharField("nom", max_length=20, default="")
    role = models.CharField("fonction", max_length=20, blank=True, default="")
    institution = models.CharField("institution", max_length=20, blank=True, default="")
    phone = models.CharField("téléphone", max_length=20, default="")
    email = models.EmailField(blank=True, default="")


    class Meta:
        verbose_name = "Tuteur"
        verbose_name_plural = "Tuteurs"

    def __str__(self):
        return "%s %s" % (self.last_name, self.first_name)

class Convention(models.Model):
    tutor = models.ForeignKey(Tuteur, verbose_name="Tuteur")
    teacher = models.ForeignKey(Professeur, verbose_name="Professeur")
    student = models.ForeignKey(Eleve, verbose_name="Stagiaire")
    stage = models.CharField(max_length=50, choices = CHOIX_STAGE)
    date_start = models.DateField("Date de début")
    date_end = models.DateField("Date de fin")
    periods = models.IntegerField("Nombre de périodes")

    def clean(self):
        if self.date_end <= self.date_start:
            raise ValidationError("La date de fin doit être après la date de début")

        this_student_other_conventions = Convention.objects.filter(student=self.student)
        for c in [other_c for other_c in this_student_other_conventions if other_c.id != self.id ]:
            if (self.date_start < c.date_start < self.date_end) or (self.date_start < c.date_end < self.date_end):
                raise ValidationError("Une autre convention entre en conflit sur cette période")


    class Meta:
        verbose_name = "Convention"
        verbose_name_plural = "Conventions"

    def __str__(self):
        return "%s - %s %s - du %s au %s" % (
            self.stage,
            self.student.last_name,
            self.student.first_name,
            self.date_start.strftime("%d/%m/%Y"),
            self.date_end.strftime("%d/%m/%Y"),
            )


class Periode(models.Model):
    convention = models.ForeignKey(Convention, on_delete=models.CASCADE)
    time_start = models.DateTimeField("Heure de début")
    time_end = models.DateTimeField("Heure de fin")

    def clean(self):
        period_date_start = date(self.time_start.year, self.time_start.month, self.time_start.day)
        period_date_end = date(self.time_end.year, self.time_end.month, self.time_end.day)

        if (period_date_start < self.convention.date_start) or (period_date_start > self.convention.date_end):
            raise ValidationError("La plage débute hors de la convention")

        if (period_date_end > self.convention.date_end):
            raise ValidationError("La plage se termine après la fin de la convention")

        if self.time_end <= self.time_start:
            raise ValidationError("La fin de la plage doit être après le début")

        this_convention_other_periods = Periode.objects.filter(convention=self.convention)
        for p in [other_p for other_p in this_convention_other_periods if other_p.id != self.id]:
            if (self.time_start < p.time_start <self.time_end) or (self.time_start < p.time_end <self.time_end):
                raise ValidationError("Les plages horaires ne peuvent se chevaucher")


    class Meta:
        verbose_name = "Plage horaire"
        verbose_name_plural = "Plages horaires"

    def __str__(self):
        return "%s -> %s" % (self.time_start.strftime("%d/%m/%Y %H:%M"), self.time_end.strftime("%d/%m/%Y %H:%M"))

@receiver(pre_save, sender=Convention)
@receiver(pre_save, sender=Periode)
def pre_save_handler(sender, instance, *args, **kwargs):
    instance.clean()
