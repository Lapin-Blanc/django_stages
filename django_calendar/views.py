from datetime import date, datetime, timedelta
from django.utils import timezone

from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.utils import timezone
from django.core.exceptions import ValidationError

from .models import Eleve, Convention
from .forms import ConventionForm

# Create your views here.
@login_required(login_url="/calendar_login/")
def accueil(request):
    context = {
    "is_teacher": Group.objects.get(name="Professeurs") in request.user.groups.all(),
    }
    if request.user.is_staff:
        return redirect('/admin/')
    else:
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
                    type_stage = c_form.cleaned_data["type_stage"]
                    new_c = Convention(
                        student=eleve,
                        place=place,
                        teacher=teacher,
                        stage=stage,
                        type_stage=type_stage,
                        date_start=datetime.today(),
                    )
                    new_c.save()
                    return HttpResponseRedirect("/horaires/")
                else:
                    return render(request, "eleves.html", { "form" : c_form })
            context["form"] = ConventionForm()
        return render(request, "eleves.html", context=context)

    elif Group.objects.get(name="Professeurs") in request.user.groups.all():
        return render(request, "professeurs.html")

    else:
        raise Exception("Horaires demandés pour un utilisateur ni élève, ni professeur")

@login_required(login_url="/calendar_login/")
def calendar_home(request):
    return render(request, "horaires.html")

# ajax
def get_events(request):
    c = manage_ajax_request(request)
    if isinstance(c, JsonResponse):
        # Il y a eu un problème
        return c
    # TODO filter based on query
    periodes = c.periode_set.all().values("id", "start", "end")
    return JsonResponse(list(periodes), safe=False)


def create_event(request):
    print("CREATE CALLED")
    c = manage_ajax_request(request)
    if isinstance(c, JsonResponse):
        # Il y a eu un problème
        return c
    start = timezone.make_aware(datetime.fromtimestamp(int(request.GET['start'])//1000))
    end = timezone.make_aware(datetime.fromtimestamp(int(request.GET['end'])//1000))
    try:
        p = c.periode_set.create(start=start, end=end)
    except ValidationError as e:
        return JsonResponse(
            {
              "errors": [
                {
                  "status": "422",
                  "source": { "pointer": request.path },
                  "detail": "%s" % e.args[0]
                },
              ]
            },
        status=400)
    # Utilisateur OK
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
    evt = c.periode_set.get(id=request.GET['event_id'])
    evt.start = evt.start + timedelta(seconds=int(request.GET['delta'])//1000)
    evt.end = evt.end + timedelta(seconds=int(request.GET['delta'])//1000)
    try:
        evt.save()
    except ValidationError as e:
        return JsonResponse(
            {
              "errors": [
                {
                  "status": "422",
                  "source": { "pointer": request.path },
                  "detail": "%s" % e.args[0]
                },
              ]
            },
        status=400)

    return JsonResponse({"result" : "OK"}, safe=False)

def resize_event(request):
    c = manage_ajax_request(request)
    if isinstance(c, JsonResponse):
        # Il y a eu un problème
        return c
    evt = c.periode_set.get(id=request.GET['event_id'])
    evt.end = evt.end + timedelta(seconds=int(request.GET['delta'])//1000)
    try:
        evt.save()
    except ValidationError as e:
        return JsonResponse(
            {
              "errors": [
                {
                  "status": "422",
                  "source": { "pointer": request.path },
                  "detail": "%s" % e.args[0]
                },
              ]
            },
        status=400)
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
            convention = request.user.eleve.get_convention()
            return convention
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
