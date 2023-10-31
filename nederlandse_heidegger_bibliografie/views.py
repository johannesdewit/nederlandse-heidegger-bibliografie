from django.shortcuts import render

from .models import BibEntry

def detail(request, bib_id):
    bib_entry = BibEntry.objects.get(id=bib_id)
    context = {"bib_entry": bib_entry}
    return render(request, "nederlandse_heidegger_bibliografie/detail.html", context)

def index(request):
    bibliography = BibEntry.objects.order_by("id")
    context = {"bibliography": bibliography}
    return render(request, "nederlandse_heidegger_bibliografie/index.html", context)