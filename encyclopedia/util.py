import re

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


# Enter directory name relative to BASE_DIR
ENTRIES_DIR_NAME = "entries"


def list_entries():
    """
    Returns a list of all names of encyclopedia entries.
    """
    _, filenames = default_storage.listdir(ENTRIES_DIR_NAME)
    return list(sorted(re.sub(r"\.md$", "", filename)
                for filename in filenames if filename.endswith(".md")))


def save_entry(title, content):
    """
    Saves an encyclopedia entry, given its title and Markdown
    content. If an existing entry with the same title already exists,
    it is replaced.
    """
    filename = f"{ENTRIES_DIR_NAME}/{title}.md"
    if default_storage.exists(filename):
        default_storage.delete(filename)
    default_storage.save(filename, ContentFile(content))


def get_entry(title):
    """
    Retrieves an encyclopedia entry (utf-8 decoded) by its title. If no such
    entry exists, the function returns None.
    """
    try:
        f = default_storage.open(f"{ENTRIES_DIR_NAME}/{title}.md")
        return f.read().decode("utf-8")
    except FileNotFoundError:
        return None


def delete_all_entries():
    """
    Deletes all the entries. Returns True if all the entries are deleted.
    If no entries are found the function returns None. 
    """
    entries_title = list_entries()
    if entries_title:
        for entry_title in entries_title:
            default_storage.delete(f"{ENTRIES_DIR_NAME}/{entry_title}.md")
        return True
    else:
        return None
