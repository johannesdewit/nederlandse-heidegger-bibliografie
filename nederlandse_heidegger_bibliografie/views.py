from django.shortcuts import render

from .models import BibEntry

def entry(request, bib_id):
    bib_entry = BibEntry.objects.get(id=bib_id)
    context = {"bib_entry": bib_entry}
    return render(request, "nederlandse_heidegger_bibliografie/entry.html", context)

def home(request):
    bibliography = BibEntry.objects.order_by("id")
    context = {"bibliography": bibliography}
    return render(request, "nederlandse_heidegger_bibliografie/home.html", context)