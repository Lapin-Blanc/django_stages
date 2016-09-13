from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def index(request):
    return HttpResponse("""
    <!DOCTYPE html>
    <html>
        <title>Accueil</title>
        <body>
        <h2>Gestion des stages EICA</h2>
        </body>
    </html>
    """)

def calendar_home(request):
    pass
