from datetime import date

from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.urls import reverse
from .models import Convention

# Create your views here.
@login_required(login_url="calendar_login/")
def calendar_home(request):
    return render(request, "calendar.html")

def get_events(request):
    if not request.user.is_authenticated:
        return JsonResponse(
            {
              "errors": [
                {
                  "status": "403",
                  "source": { "pointer": reverse("get_events") },
                  "detail": "Vous n'avez pas le droit de consulter cette ressource"
                },
              ]
            },
        status=400)
    else:
        if Group.objects.get(name="Élèves") in request.user.groups.all():
            conventions = request.user.eleve.convention_set.filter(date_start__lte=date.today(), date_end__gte=date.today())
            if len(conventions) > 1:
                return JsonResponse(
                    {
                      "errors": [
                        {
                          "status": "403",
                          "source": { "pointer": reverse("get_events") },
                          "detail": "Plus d'une conventions !"
                        },
                      ]
                    },
                status=400)
            elif len(conventions) == 0:
                return JsonResponse(
                    {
                      "errors": [
                        {
                          "status": "403",
                          "source": { "pointer": reverse("get_events") },
                          "detail": "Pas de convention pour cette date"
                        },
                      ]
                    },
                status=400)
            else:
                # OK, une convention sélectionnée
                convention = conventions[0]
                # TODO filter based on query
                periodes = convention.periode_set.all().values("id", "start", "end")
                return JsonResponse(list(periodes), safe=False)
