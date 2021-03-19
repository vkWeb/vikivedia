from django.shortcuts import render
from django.http import HttpResponse, Http404, HttpResponseRedirect, HttpResponseBadRequest, HttpResponseNotAllowed
from django.urls import reverse
from django.contrib import messages

from . import util
from .safematter import ALLOWED_TAGS, ALLOWED_ATTRS

import markdown2
import random
import bleach

# Seed random number generator
random.seed()

# DEBUG
count = 0
print(f"{count}. views.py is run")
count += 1
# END_DEBUG


def wiki_redirect(request):
    return HttpResponseRedirect(reverse("encyclopedia:root"))


# Homepage view
def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })


# Returns data of an entry
# Do heavy XSS testing for this view
def entry(request, title):
    entry = util.get_entry(title)
    if entry:
        markdowner = markdown2.Markdown()
        html = markdowner.convert(entry)
        sanitizer = bleach.sanitizer.Cleaner(tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRS, strip=False, strip_comments=False)
        html = sanitizer.clean(html)

        return render(request, "encyclopedia/entry.html", {
            "title": title,
            "html": html
        })

    raise Http404("Entry not found")


# Handle new entry creation
def new_entry(request):
    if request.method == "POST":
        title = request.POST["entry-title"].strip()
        content = request.POST["entry-content"].strip()

        if title and content:

            # If we already have an entry then report error to client
            if util.get_entry(title):
                return render(request, "encyclopedia/create-new-entry.html", {
                    "error_msg": {
                        "title_error": "An entry already exists with the provided title. Please provide another title."
                        },
                    "entry_title": title,
                    "entry_content": content
                    })
            else:
                util.save_entry(title, content)
                messages.success(request, "Congratulations! You successfully created a new article.")
                return HttpResponseRedirect(reverse("encyclopedia:wikititle", args=(title,)))

        # Either title or content was not provided by the client, report appropriately
        else:
            is_entry_title = True
            is_entry_content = True

            if not title:
                is_entry_title = False
            if not content:
                is_entry_content = False

            return render(request, "encyclopedia/create-new-entry.html", {
                "is_entry_title_ok": is_entry_title,
                "is_entry_content": is_entry_content,
                "error_msg": {
                    "title_error": "Please provide title.",
                    "content_error": "Please provide content."
                    },
                "entry_title": title,
                "entry_content": content
            })

    elif request.method == "GET":
        return render(request, "encyclopedia/create-new-entry.html")

    # If the method is not GET or POST, we want the client to know that
    else:
        raise HttpResponseNotAllowed(["GET", "POST"])


# Return a random article
def random_entry(request):
    entries_title = util.list_entries()

    try:
        random_title = random.choice(entries_title)
    except IndexError:
        messages.error(request, "Sorry, we didn't find any entry at all.")
        return HttpResponseRedirect(reverse("encyclopedia:root"))
    else:
        return HttpResponseRedirect(reverse("encyclopedia:wikititle", args=(random_title,)))


# Edit an already existing entry
def edit_entry(request, title):
    if request.method == "GET":
        entry_content = util.get_entry(title)
        if not entry_content:
            raise Http404

        return render(request, "encyclopedia/create-new-entry.html", {
            "is_edit_entry": True,
            "entry_title": title,
            "entry_content": entry_content
            })

    elif request.method == "POST":
        is_title_ok = True
        is_content = True
        POST_title = request.POST["entry-title"].strip()
        POST_content = request.POST["entry-content"].strip()

        if title != POST_title:
            is_title_ok = False
        if not POST_content:
            is_content = False

        if title == POST_title and POST_content:
            util.save_entry(title, POST_content)
            messages.success(request, "You successfully edited the entry.")
            return HttpResponseRedirect(reverse("encyclopedia:wikititle", args=(title,)))
        else:
            return render(request, "encyclopedia/create-new-entry.html", {
                "is_edit_entry": True,
                "entry_title": title,
                "entry_content": POST_content,
                "is_entry_title_ok": is_title_ok,
                "is_entry_content": is_content,
                "error_msg": {
                    "title_error": "You changed the title. Save again without changing the title!",
                    "content_error": "Ohh no! we hate emptiness. Fill the content with some love <3"
                    }
                })
    # If the method is not GET or POST, we want client to know that
    else:
        raise HttpResponseNotAllowed(["GET", "POST"])


# Search functionality
def search(request):
    try:
        query = request.GET.get("q").strip().lower()
    except AttributeError:
        messages.info(request, "No search query was provided.")
        return HttpResponseRedirect(reverse("encyclopedia:root"))

    if query:
        entries = util.list_entries()
        result = []
        for entry in entries:
            if entry.lower() == query:
                return HttpResponseRedirect(reverse("encyclopedia:wikititle", args=(entry,)))
            if entry.lower().find(query) != -1:
                result.append(entry)

        if not result:
            messages.error(request, "Sorry, no entry found for that search query. Try another one!")
        else:
            return render(request, "encyclopedia/index.html", {
                "is_search": True,
                "entries": result
                })

    return HttpResponseRedirect(reverse("encyclopedia:root"))


# Delete all entries functionality
def delete_all_entries(request):
    if request.method == "POST":
        choice = request.POST.get("choice", False)
        if choice == False:
            messages.error(request, "No option was selected. Please select an option.")
            return HttpResponseRedirect(reverse("encyclopedia:deleteallentries"))
        if choice == "0":
            messages.info(request, "Nothing was deleted on your command, sir!")
        elif choice == "1":
            if util.delete_all_entries() == True:
                messages.success(request, "Deleted all the entries, sad to see them going :(")
            else:
                messages.error(request, "No entry exist.")
        return HttpResponseRedirect(reverse("encyclopedia:root"))
    elif request.method == "GET":
        return render(request, "encyclopedia/delete-all-entries.html")
    else:
        raise HttpResponseNotAllowed(["GET", "POST"])
