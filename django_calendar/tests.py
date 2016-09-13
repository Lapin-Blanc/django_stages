from datetime import date, datetime
from pytz import timezone

from django.test import TestCase
from django.contrib.auth.models import User, Group
from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db.utils import IntegrityError
from .models import Eleve, Professeur, Tuteur, Convention, Period


tz = timezone("Europe/Brussels")

class UserTests(TestCase):
    fixtures = ["base_profs_eleves.json"]
    def test_can_create_tutor(self):
        t = Tuteur(
            first_name = "Bob",
            last_name = "Morane",
            institution = "La sérénité",
            role = "Chef de service",
            phone = "123465",
            email = "bob.morane@serenite.be"
            )
        t.save()
        self.assertEqual(str(t), "Morane Bob")

    def test_can_create_eleve(self):
        e = Eleve(username="john.doe", password="the_password")
        e.save()
        u = User.objects.get(username="john.doe")
        self.assertIs(u.check_password("the_password"), True)

    def test_eleve_username_is_unique(self):
        e1 = Eleve(username="john.doe", password="the_password")
        e1.save()
        e2 = Eleve(username="john.doe", password="the_password")
        self.assertRaises(IntegrityError, e2.save)

    def test_can_update_eleve(self):
        # create eleve
        e = Eleve(username="john.doe", password="the_password")
        e.save()
        # modify eleve
        e = Eleve.objects.get(username="john.doe")
        e.username="jane.doe"
        e.first_name = "Jane"
        e.last_name = "Doe"
        e.password = "new_password"
        e.save()
        # verify update
        u = User.objects.get(username="jane.doe")
        self.assertEqual(u.first_name, "Jane")
        self.assertEqual(u.last_name, "Doe")
        self.assertTrue(u.check_password("new_password"))

    def test_delete_eleve_with_user(self):
        e = Eleve(username="john.doe", password="the_password")
        e.save()
        u = User.objects.get(username="john.doe")
        u.delete()
        self.assertRaises(ObjectDoesNotExist, Eleve.objects.get, username="john.doe")

    def test_delete_user_with_eleve(self):
        e = Eleve(username="john.doe", password="the_password")
        e.save()
        f = Eleve.objects.get(username="john.doe")
        f.delete()
        self.assertRaises(ObjectDoesNotExist, User.objects.get, username="john.doe")

    def test_users_in_their_groups(self):
        e = Eleve(username="john.doe", password="the_password")
        e.save()
        p = Professeur(username="albert.einstein", password="emc2")
        p.save()
        self.assertIn(Group.objects.get(name="Élèves"), e.user.groups.all())
        self.assertIn(Group.objects.get(name="Professeurs"), p.user.groups.all())

class ConventionTest(TestCase):
    fixtures = ["base_profs_eleves.json"]
    def test_can_create_convention(self):
        t = Tuteur(
            first_name = "Bob",
            last_name = "Morane",
            institution = "La sérénité",
            role = "Chef de service",
            phone = "123465",
            email = "bob.morane@serenite.be"
            )
        t.save()
        c = Convention(
            tutor = t,
            teacher = Professeur.objects.get(username="karine.demine"),
            student = Eleve.objects.get(username="fabien.toune"),
            stage = "Stage d'observation",
            date_start = date(2016, 6, 16),
            date_end = date(2016,10, 30),
            periods = 200
            )
        c.save()
        self.assertEqual(str(c), "Stage d'observation - Toune Fabien - 2016:2016")

    def test_convention_ends_after_start(self):
        t = Tuteur(
            first_name = "Bob",
            last_name = "Morane",
            institution = "La sérénité",
            role = "Chef de service",
            phone = "123465",
            email = "bob.morane@serenite.be"
            )
        t.save()
        c = Convention(
            tutor = t,
            teacher = Professeur.objects.get(username="karine.demine"),
            student = Eleve.objects.get(username="fabien.toune"),
            stage = "Stage d'observation",
            date_start = date(2016, 10, 16),
            date_end = date(2016, 9, 30),
            periods = 200
            )
        self.assertRaisesMessage(ValidationError, "La date de fin doit être après la date de début", c.save)

    def test_conventions_cant_overlap_for_one_student(self):
        t = Tuteur(
            first_name = "Bob",
            last_name = "Morane",
            institution = "La sérénité",
            role = "Chef de service",
            phone = "123465",
            email = "bob.morane@serenite.be"
            )
        t.save()
        c1 = Convention(
            tutor = t,
            teacher = Professeur.objects.get(username="karine.demine"),
            student = Eleve.objects.get(username="fabien.toune"),
            stage = "Stage d'observation",
            date_start = date(2016, 1, 1),
            date_end = date(2016, 6, 30),
            periods = 200
            )
        c2 = Convention(
            tutor = t,
            teacher = Professeur.objects.get(username="karine.demine"),
            student = Eleve.objects.get(username="fabien.toune"),
            stage = "Stage d'observation",
            date_start = date(2016, 5, 1),
            date_end = date(2016, 7, 31),
            periods = 200
            )
        c1.save()
        self.assertRaisesMessage(ValidationError, "Une autre convention entre en conflit sur cette période", c2.save)
        c2.date_start = date(2015, 6, 30)
        c2.date_end = date(2016, 1, 2)
        self.assertRaisesMessage(ValidationError, "Une autre convention entre en conflit sur cette période", c2.save)
        c2.date_end = date(2016, 1, 1)
        c2.save()
        self.assertEqual(str(c2), "Stage d'observation - Toune Fabien - 2015:2016")

class HoraireTest(TestCase):
    fixtures = ["base_profs_eleves.json"]
    def test_can_create_period(self):
        t = Tuteur(
            first_name = "Bob",
            last_name = "Morane",
            institution = "La sérénité",
            role = "Chef de service",
            phone = "123465",
            email = "bob.morane@serenite.be"
            )
        t.save()
        c = Convention(
            tutor = t,
            teacher = Professeur.objects.get(username="karine.demine"),
            student = Eleve.objects.get(username="fabien.toune"),
            stage = "Stage d'observation",
            date_start = date(2016, 10, 15),
            date_end = date(2016, 12, 31),
            periods = 200
            )
        c.save()
        p = Period(
            convention = c,
            time_start = datetime(2016, 9, 13, 9, 0, 0, tzinfo=tz),
            time_end = datetime(2016, 9, 13, 16, 30, 0, tzinfo=tz),
            )
        p.save()
        self.assertEqual(str(p), "13/09/2016 09:00 -> 13/09/2016 16:30")

    def test_plages_horaires_must_ends_after_start(self):
        t = Tuteur(
            first_name = "Bob",
            last_name = "Morane",
            institution = "La sérénité",
            role = "Chef de service",
            phone = "123465",
            email = "bob.morane@serenite.be"
            )
        t.save()
        c = Convention(
            tutor = t,
            teacher = Professeur.objects.get(username="karine.demine"),
            student = Eleve.objects.get(username="fabien.toune"),
            stage = "Stage d'observation",
            date_start = date(2016, 10, 15),
            date_end = date(2016, 12, 31),
            periods = 200
            )
        c.save()
        p = Period(
            convention = c,
            time_start = datetime(2016, 9, 13, 17, 0, 0, tzinfo=tz),
            time_end = datetime(2016, 9, 13, 16, 30, 0, tzinfo=tz),
            )
        self.assertRaisesMessage(ValidationError, "La fin de la plage doit être après le début", p.save)

    def test_plages_horaires_cant_overlap(self):
        t = Tuteur(
            first_name = "Bob",
            last_name = "Morane",
            institution = "La sérénité",
            role = "Chef de service",
            phone = "123465",
            email = "bob.morane@serenite.be"
            )
        t.save()
        c = Convention(
            tutor = t,
            teacher = Professeur.objects.get(username="karine.demine"),
            student = Eleve.objects.get(username="fabien.toune"),
            stage = "Stage d'observation",
            date_start = date(2016, 10, 15),
            date_end = date(2016, 12, 31),
            periods = 200
            )
        c.save()
        p1 = Period(
            convention = c,
            time_start = datetime(2016, 9, 13, 9, 0, 0, tzinfo=tz),
            time_end = datetime(2016, 9, 13, 16, 30, 0, tzinfo=tz),
            )
        p1.save()
        p2 = Period(
            convention = c,
            time_start = datetime(2016, 9, 13, 16, 0, 0, tzinfo=tz),
            time_end = datetime(2016, 9, 13, 17, 0, 0, tzinfo=tz),
            )
        self.assertRaisesMessage(ValidationError, "Les plages horaires ne peuvent se chevaucher", p2.save)
        p2.time_start = datetime(2016, 9, 13, 8, 0, 0, tzinfo=tz)
        p2.time_end = datetime(2016, 9, 13, 9, 0, 1, tzinfo=tz)
        self.assertRaisesMessage(ValidationError, "Les plages horaires ne peuvent se chevaucher", p2.save)
        p2.time_end = datetime(2016, 9, 13, 9, 0, 0, tzinfo=tz)
        p2.save()
