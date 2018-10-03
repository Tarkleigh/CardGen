import html
import os
import subprocess
import sys
import xml.etree.ElementTree as elementTree
import CardCreator

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph


def get_entries_from_xml(xml_tree):
    entries = []

    for item in xml_tree.iter("item"):
        entry = {}

        entry["summary"] = extract_value(item, "summary")
        entry["description"] = extract_value(item, "description")
        entry["assignee"] = extract_value(item, "assignee")

        key = extract_value(item, "key")
        split = key.split("-")
        entry["project"] = split[0]
        entry["key"] = split[1]

        entry["priority"] = extract_value(item, "priority")
        entry["rank"] = extract_rank_from_custom_fields(item)

        remove_null_values(entry)

        for key in entry.keys():
            entry[key] = remove_link_tags(entry[key])
            entry[key] = check_and_escape(entry[key])

        entries.append(entry)

    return entries


def extract_value(item, key):
    value = item.find(key).text
    if value is None:
        value = ""

    return value


def initialize_tkinter():
    import tkinter as tk
    root = tk.Tk()
    root.withdraw()


def check_and_escape(string):
    # reportLab can't handle gifs (they cause a hard crash), escape if one is present
    try:
        Paragraph(string, getSampleStyleSheet()['BodyText'])
        return string
    except ValueError:
        return html.escape(string)


def remove_excessive_new_lines(string):
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


def remove_null_values(entry):
    for key in entry.keys():
        if entry[key] is None:
            entry[key] = ''


def remove_link_tags(string):
    tag_start_index = string.find("<a href")
    while tag_start_index != -1:
        end_index = string.find("</a>", tag_start_index)
        string = string[0:tag_start_index] + " <i>link</i> " + string[end_index + 4:]
        tag_start_index = string.find("<a href")
    return string


def extract_rank_from_custom_fields(item):
    rank = "0"
    for custom_field in item.iter("customfield"):
        if custom_field.find("customfieldname").text == "Rank":
            for values in custom_field.iter("customfieldvalue"):
                rank = values.text

    return rank


def open_output_file(file_path):
    if sys.platform == "win32":
        os.startfile(file_path)
    elif sys.platform == "darwin":  # mac
        subprocess.call(["open", file_path])
    else:  # linux
        subprocess.call(["xdg-open", file_path])


def get_file_paths():
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        import tkinter.filedialog as file_dialog
        initialize_tkinter()
        file_path = file_dialog.askopenfilename()

    output_path = file_path[:-3] + "pdf"
    return file_path, output_path


def main():
    file_path, output_path = get_file_paths()
    xml_tree = elementTree.parse(file_path)
    entries = get_entries_from_xml(xml_tree)

    creator = CardCreator.Converter(output_path)
    creator.create_pdf(entries)
    open_output_file(output_path)


if __name__ == '__main__':
    main()
