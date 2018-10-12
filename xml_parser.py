"""Reads a given XML and passed its values to card_generator.py to create a pdf of cards.
Once the generation is complete, the created pdf file will be opened automatically with the
standard programme for this file type"""
import html
import os
import subprocess
import sys
import xml.etree.ElementTree as elementTree

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph

import card_generator


def get_entries_from_xml(xml_tree):
    """Convert xml data to a list of dictionaries, with one entry for each backlog item."""
    entries = []

    for item in xml_tree.iter("item"):
        entry = {}

        entry["summary"] = extract_value(item, "summary")
        entry["assignee"] = extract_value(item, "assignee")
        entry["description"] = extract_description(item)

        key = extract_value(item, "key")
        key_parts = key.split("-")
        entry["key"] = key_parts[1]

        entry["priority"] = extract_value(item, "priority")
        entry["rank"] = extract_rank_from_custom_fields(item)

        entries.append(entry)

    return entries


def extract_description(item):
    """Extract description of item"""
    description = extract_value(item, "description")
    description = remove_excessive_new_lines(description)
    description = trim_description(description)

    return description


def trim_description(description):
    """Trim description, if it is longer than 160 characters."""
    if len(description) > 160:
        description = description[0:161] + '...'
    return description


def extract_value(item, key):
    """Get the value for the given key or return an empty string if no value is found."""
    value = item.find(key).text
    if value is None:
        value = ""
    else:
        value = sanitize_value(value)
    return value


def sanitize_value(value):
    """Remove values that would break card generation."""
    value = remove_link_tags(value)
    value = check_and_escape(value)
    return value


def initialize_tkinter():
    """Load tkinter for file choosing dialog."""
    import tkinter as tk
    root = tk.Tk()
    root.withdraw()


def check_and_escape(string):
    """Check if string can be used by Reportlab and escape if needed."""
    # reportLab can't handle gifs (they cause a hard crash), so we try to create a Paragraph
    # and escape if this doesn't work
    try:
        Paragraph(string, getSampleStyleSheet()['BodyText'])
        return string
    except ValueError:
        return html.escape(string)


def remove_excessive_new_lines(string):
    """Change string so there are at most four line breaks."""
    newlines = 0
    index = string.find('\n')

    while index != -1:
        newlines += 1
        if newlines >= 4:
            # snip string after the fourth new line
            return string[:index]
        index = string.find('\n', index + 1)

    # not too many new lines, return string unchanged
    return string


def remove_link_tags(string):
    """Remove link tags in string."""
    tag_start_index = string.find("<a href")
    while tag_start_index != -1:
        end_index = string.find("</a>", tag_start_index)
        string = string[0:tag_start_index] + " <i>link</i> " + string[end_index + 4:]
        tag_start_index = string.find("<a href")
    return string


def extract_rank_from_custom_fields(item):
    """Get the rank value from the custom fields."""
    rank = "0"
    for custom_field in item.iter("customfield"):
        if custom_field.find("customfieldname").text == "Rank":
            for values in custom_field.iter("customfieldvalue"):
                rank = values.text

    rank = sanitize_value(rank)
    return rank


def open_output_file(file_path):
    """Open created PDF file."""
    if sys.platform == "win32":
        os.startfile(file_path)
    elif sys.platform == "darwin":  # mac
        subprocess.call(["open", file_path])
    else:  # linux
        subprocess.call(["xdg-open", file_path])


def get_file_paths():
    """Get input and output paths needed for generation."""
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        import tkinter.filedialog as file_dialog
        initialize_tkinter()
        file_path = file_dialog.askopenfilename()

    output_path = file_path[:-3] + "pdf"
    return file_path, output_path


def main():
    """Start card generation."""
    file_path, output_path = get_file_paths()
    xml_tree = elementTree.parse(file_path)
    entries = get_entries_from_xml(xml_tree)

    creator = card_generator.Generator()
    creator.create_pdf(entries, output_path)
    open_output_file(output_path)


if __name__ == '__main__':
    main()
