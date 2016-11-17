from datetime import date, datetime, timedelta
from django.utils import timezone

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.utils import timezone

from .models import Eleve, Convention
from .forms import ConventionForm

# Create your views here.
@login_required(login_url="/calendar_login/")
def accueil(request):
    context = {
    "is_teacher": Group.objects.get(name="Professeurs") in request.user.groups.all(),
    }
    return render(request, "accueil.html", context=context)

@login_required(login_url="/calendar_login/")
def horaires(request):
    context = {}
    if Group.objects.get(name="Élèves") in request.user.groups.all():
        eleve = Eleve.objects.get(user=request.user)
        context["eleve"] = eleve
        c = eleve.get_convention()
        if c:
            context["convention"] = c
        else:
            if request.method == "POST":
                c_form = ConventionForm(request.POST)
                if c_form.is_valid():
                    place = c_form.cleaned_data["place"]
                    teacher = c_form.cleaned_data["teacher"]
                    stage = c_form.cleaned_data["stage"]
                    new_c = Convention(
                        student=eleve,
                        place=place,
                        teacher=teacher,
                        stage=stage,
                        date_start=datetime.today(),
                    )
                    new_c.save()
                    return HttpResponseRedirect("/horaires/")
            context["form"] = ConventionForm()
        return render(request, "eleves.html", context=context)

    elif Group.objects.get(name="Professeurs") in request.user.groups.all():
        return render(request, "professeurs.html")

    else:
        raise Exception("Horaires demandés pour un utilisateur ni élève, ni professeur")

@login_required(login_url="/calendar_login/")
def calendar_home(request):
    return render(request, "horaires.html")

def get_events(request):
    c = manage_ajax_request(request)
    if isinstance(c, JsonResponse):
        # Il y a eu un problème
        return c
    # TODO filter based on query
    periodes = c.periode_set.all().values("id", "start", "end")
    return JsonResponse(list(periodes), safe=False)


# ajax
def create_event(request):
    print("CREATE CALLED")
    c = manage_ajax_request(request)
    if isinstance(c, JsonResponse):
        # Il y a eu un problème
        return c
    start = timezone.make_aware(datetime.fromtimestamp(int(request.GET['start'])//1000))
    end = timezone.make_aware(datetime.fromtimestamp(int(request.GET['end'])//1000))
    p = c.periode_set.create(start=start, end=end)
    return JsonResponse({"event_id" : p.id}, safe=False)


def delete_event(request):
    c = manage_ajax_request(request)
    if isinstance(c, JsonResponse):
        # Il y a eu un problème
        return c
    msg = c.periode_set.get(id=request.GET['event_id']).delete()
    return JsonResponse({"message" : msg}, safe=False)

def move_event(request):
    c = manage_ajax_request(request)
    if isinstance(c, JsonResponse):
        # Il y a eu un problème
        return c
    e = c.periode_set.get(id=request.GET['event_id'])
    e.start = e.start + timedelta(seconds=int(request.GET['delta'])//1000)
    e.end = e.end + timedelta(seconds=int(request.GET['delta'])//1000)
    e.save()
    return JsonResponse({"result" : "OK"}, safe=False)

def resize_event(request):
    c = manage_ajax_request(request)
    if isinstance(c, JsonResponse):
        # Il y a eu un problème
        return c
    e = c.periode_set.get(id=request.GET['event_id'])
    e.end = e.end + timedelta(seconds=int(request.GET['delta'])//1000)
    e.save()
    return JsonResponse({"result" : "OK"}, safe=False)

#############################################################
def manage_ajax_request(request):
    # retourne un objet convention si tout va bien, gère les erreur ajax sinon
    # Utilisateur non identifié -> on refuse
    if not request.user.is_authenticated:
        return JsonResponse(
            {
              "errors": [
                {
                  "status": "403",
                  "source": { "pointer": request.path },
                  "detail": "Access denied"
                },
              ]
            },
        status=400)
    # Utilisateur OK
    else :
        if Group.objects.get(name="Élèves") in request.user.groups.all():
            # On a affaire à un élève
            conventions_courantes = request.user.eleve.convention_set.filter(date_start__lte=date.today(), date_end__gte=date.today())
            if len(conventions_courantes) > 1 :
                # Trop de convention pour cet élève à cette date (impossible normalement par validation des données)
                return JsonResponse(
                    {
                      "errors": [
                        {
                          "status": "400",
                          "source": { "pointer": request.path },
                          "detail": "Too many conventions"
                        },
                      ]
                    },
                status=400)
            elif len(conventions_courantes) == 0 :
                # Pas de convention pour cet élève à ce jour
                return JsonResponse(
                    {
                      "errors": [
                        {
                          "status": "404",
                          "source": { "pointer": request.path },
                          "detail": "No conventions"
                        },
                      ]
                    },
                status=404)
            else:
                # OK, on tient une convention
                convention_courante = conventions_courantes[0]
                # TODO filter based on request's params
                #periodes = convention.periode_set.all().values("id", "start", "end")
                #return JsonResponse(list(periodes), safe=False)
                return convention_courante

        #elif Group.objects.get(name="Professeurs") in request.user.groups.all():
            # On a affaire à un Professeurs
            #pass

        else:
            # l'utilisateur n'est ni élève, ni professeur
            return JsonResponse(
                {
                  "errors": [
                    {
                      "status": "403",
                      "source": { "pointer": request.path },
                      "detail": "Access denied"
                    },
                  ]
                },
            status=403)
