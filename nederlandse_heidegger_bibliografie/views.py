from django.shortcuts import render

from .models import Author, BibEntry

def entry(request, bib_id):
    bib_entry = BibEntry.objects.get(id=bib_id)
    context = {"bib_entry": bib_entry}
    return render(request, "nederlandse_heidegger_bibliografie/entry.html", context)

def home(request):
    #TODO: Filter out duplicates returned by this query.
    bibliography = BibEntry.objects.all()
    context = {"bibliography": bibliography}
    return render(request, "nederlandse_heidegger_bibliografie/home.html", context)

def author(request, author_id):
    author = Author.objects.get(id=author_id)
    context = {"author": author}
    return render(request, "nederlandse_heidegger_bibliografie/author.html", context)