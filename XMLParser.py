import random
import html
import sys
import subprocess
import os
import xml.etree.ElementTree as elementTree
import reportlab.lib.pagesizes as sizes
import reportlab.lib.units as layout_units
import reportlab.pdfgen.canvas as pdf_canvas
from reportlab.lib import colors as reportlab_colors
from reportlab.platypus import Table, TableStyle
from reportlab.platypus import Frame
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet


class Converter():
    def __init__(self):
        self.start_x = 10
        self.start_y = 325
        self.frame_count = 1
        self.file_path = ""
        self.output_path = ""

        self.colors = []
        self.used_colors = {}
        self.styles = {}
        self.royal_blue = (0 / 256, 85 / 256, 164 / 256)
        self.bavarian_red = (223 / 256, 33 / 256, 39 / 256)
        self.bvb_yellow = (255 / 256, 232 / 256, 0 / 256)

    def main(self):
        self.get_file_paths()
        xml_tree = elementTree.parse(self.file_path)

        entries = self.get_entries_from_xml(xml_tree)
        self.create_pdf(entries)
        self.open_output_file(self.output_path)

    def get_file_paths(self):
        if len(sys.argv) > 1:
            self.file_path = sys.argv[1]
        else:
            import tkinter.filedialog as fileDialog
            Converter.initialize_tkinter(self)
            self.file_path = fileDialog.askopenfilename()

        self.output_path = self.file_path[:-3] + "pdf"

    def check_and_escape(self, string):
        # reportLab can't handle gifs (they cause a hard crash), escape if one is present
        try:
            Paragraph(string, getSampleStyleSheet()['BodyText'])
            return string
        except ValueError:
            return html.escape(string)

    def remove_excessive_new_lines(self, string):
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

    def initialize_tkinter(self):
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()

    def get_entries_from_xml(self, xml_tree):
        entries = []

        for item in xml_tree.iter("item"):
            entry = {}

            entry["summary"] = item.find("summary").text
            entry["description"] = item.find("description").text
            entry["assignee"] = item.find("assignee").text

            key = item.find("key").text
            split = key.split("-")
            entry["project"] = split[0]
            entry["key"] = split[1]

            entry["priority"] = item.find("priority").text
            entry["rank"] = self.extract_rank_from_custom_fields(item)
            entry["label"] = self.extract_label(item)

            self.extract_component(entry, item)

            self.remove_null_values(entry)
            entries.append(entry)

        return entries

    def extract_component(self, entry, item):
        component = item.find("component")
        if component is None:
            entry["component"] = ""
        else:
            entry["component"] = component.text

    def remove_null_values(self, entry):
        for key in entry.keys():
            if entry[key] == None:
                entry[key] = ''

    def extract_label(self, item):
        label = ''
        for label_tag in item.iter("labels"):
            label_value = label_tag.find("label")
            if label_value is not None:
                label = label_value.text
        return label

    def create_pdf(self, entries):
        self.load_colors()

        canvas = pdf_canvas.Canvas(filename=self.output_path, bottomup=1,
                                   pagesize=sizes.landscape(sizes.A4))

        for entry in entries:

            for key in entry.keys():
                entry[key] = self.remove_link_tags(entry[key])
                entry[key] = self.check_and_escape(entry[key])

            assignee = entry["assignee"]
            project = entry["project"]
            label = entry["label"]
            component = entry["component"]

            first_line_style = "firstLine"

            if project == "KSCPI" and component != "Document Service":
                card_color = reportlab_colors.black
                first_line_style = "firstLineAlt"
            else:
                if label == "CF":
                    card_color = self.bavarian_red
                    first_line_style = "firstLineRed"
                elif assignee == "Unassigned":
                    card_color = self.royal_blue
                    first_line_style = "firstLineStyleUnassigned"
                else:
                    card_color = self.get_card_color(assignee)

            frame_content = []
            table_data = self.get_table_data(assignee, entry, first_line_style)

            card_frame = Frame(self.start_x, self.start_y, width=14.5 * layout_units.cm,
                               height=8.5 * layout_units.cm, showBoundary=0)

            card_style = TableStyle([('BACKGROUND', (0, 0), (1, 0), card_color),
                                     ('VALIGN', (0, 0), (1, 0), "MIDDLE"),
                                     ('BOTTOMPADDING', (0, 0), (1, 0), 14),
                                     ('VALIGN', (0, 1), (-1, -1), "TOP"),
                                     ('INNERGRID', (0, 0), (-1, -1), 0.9, reportlab_colors.black),
                                     ('BOX', (0, 0), (-1, -1), 0.9, reportlab_colors.black)])

            table = Table(data=table_data, colWidths=[2.7 * layout_units.cm, 11.3 * layout_units.cm],
                          rowHeights=[1.2 * layout_units.cm, 3.4 * layout_units.cm,
                                      2.1 * layout_units.cm, 1.2 * layout_units.cm])
            table.setStyle(card_style)

            frame_content.append(table)

            card_frame.addFromList(frame_content, canvas)

            self.get_new_card_position(canvas)
        canvas.save()

    def load_colors(self):
        olive = (192 / 256, 255 / 256, 62 / 256)
        light_blue = (135 / 256, 206 / 256, 250 / 256)
        hot_pink = (255 / 256, 110 / 256, 180 / 256)
        gold = (255 / 256, 236 / 256, 139 / 256)
        salmon = (250 / 256, 128 / 256, 114 / 256)
        pale_green = (152 / 256, 251 / 256, 152 / 256)
        light_grey = (234 / 256, 234 / 256, 234 / 256)
        dark_turquoise = (0 / 256, 206 / 256, 209 / 256)
        dark_orange = (255 / 256, 140 / 256, 0 / 256)
        medium_purple = (171 / 256, 130 / 256, 255 / 256)

        self.colors = [olive, light_blue, hot_pink, gold, salmon,
                       pale_green, light_grey, dark_turquoise, dark_orange, medium_purple]

    def remove_link_tags(self, string):
        tag_start_index = string.find("<a href")
        while (tag_start_index) != -1:
            end_index = string.find("</a>", tag_start_index)
            string = string[0:tag_start_index] + " <i>link</i> " + string[end_index + 4:]
            tag_start_index = string.find("<a href")
        return string

    def get_card_color(self, assignee):
        if assignee in self.used_colors:
            card_color = self.used_colors[assignee]
        else:
            card_color = random.choice(self.colors)
            self.used_colors[assignee] = card_color
            self.colors.remove(card_color)

        return card_color

    def get_table_data(self, assignee, entry, first_line_style):

        self.load_styles()

        rank_paragraph = Paragraph(entry["rank"], self.styles[first_line_style])

        priority_paragraph = Paragraph(entry["priority"], self.styles[first_line_style])
        summary_paragraph = Paragraph(entry["summary"], self.styles["summary"])
        desc_label_paragraph = Paragraph("Description:", self.styles["label"])
        key_paragraph = Paragraph(entry["key"], self.styles["summary"])
        processor_label_paragraph = Paragraph("Processor:", self.styles["label"])

        description_string = entry.get("description", '')

        if len(description_string) > 160:
            description_string = description_string[0:161] + '...'

        description_string = self.remove_excessive_new_lines(description_string)

        try:
            description_paragraph = Paragraph(description_string, self.styles["description"])
        except ValueError:
            description_string = html.escape(description_string)
            description_paragraph = Paragraph(description_string, self.styles["description"])

        # remove "Unassigned" so people can fill out the cards themselves
        if assignee == "Unassigned":
            assignee = ""

        if len(assignee) > 30:
            processor_paragraph = Paragraph(assignee, self.styles["smallProcessor"])
        else:
            processor_paragraph = Paragraph(assignee, self.styles["processor"])

        data = [[rank_paragraph, priority_paragraph],
                [key_paragraph, summary_paragraph],
                [desc_label_paragraph, description_paragraph],
                [processor_label_paragraph, processor_paragraph]]
        return data

    def load_styles(self):
        first_line_style = ParagraphStyle(name="firstLine", fontName='Helvetica-Bold',
                                          fontSize=18, alignment=0)
        self.styles["firstLine"] = first_line_style

        first_line_style_alt = ParagraphStyle(name="firstLineAlt", fontName='Helvetica-Bold',
                                              fontSize=18, alignment=0,
                                              textColor=self.bvb_yellow)
        self.styles["firstLineAlt"] = first_line_style_alt

        first_line_style_red = ParagraphStyle(name="firstLineRed", fontName='Helvetica-Bold',
                                              fontSize=18, alignment=0,
                                              textColor=reportlab_colors.white)
        self.styles["firstLineRed"] = first_line_style_red

        first_line_style_unassigned = ParagraphStyle(name="firstLineUnassigned",
                                                     fontName='Helvetica-Bold', fontSize=18,
                                                     alignment=0, textColor=reportlab_colors.white)
        self.styles["firstLineStyleUnassigned"] = first_line_style_unassigned

        summary_style = ParagraphStyle(name="summary", fontName='Helvetica-Bold',
                                       fontSize=22, alignment=0, leading=22)
        self.styles["summary"] = summary_style

        description_style = ParagraphStyle(name="description", fontName='Helvetica',
                                           fontSize=11, alignment=0, leading=12)
        self.styles["description"] = description_style

        processor_style = ParagraphStyle(name="processor", fontName='Helvetica-Bold',
                                         fontSize=20, alignment=0)
        self.styles["processor"] = processor_style

        small_processor_style = ParagraphStyle(name="smallProcessor", fontName='Helvetica-Bold',
                                               fontSize=15, alignment=0)
        self.styles["smallProcessor"] = small_processor_style

        label_style = ParagraphStyle(name="label", fontName='Helvetica',
                                     fontSize=12, alignment=0, leftIndent=0)
        self.styles["label"] = label_style

    def get_new_card_position(self, canvas):
        if self.frame_count == 1:
            self.frame_count += 1
            self.start_x += 410
        elif self.frame_count == 2:
            self.frame_count += 1
            self.start_x = 10
            self.start_y = 75
        elif self.frame_count == 3:
            self.frame_count += 1
            self.start_x += 410
        elif self.frame_count == 4:
            self.frame_count = 1
            self.start_x = 10
            self.start_y = 325
            canvas.showPage()

    def extract_rank_from_custom_fields(self, item):
        rank = "0"
        for custom_field in item.iter("customfield"):
            if custom_field.find("customfieldname").text == "Rank":
                for values in custom_field.iter("customfieldvalue"):
                    rank = values.text
                    # replace ':' in case the rank gets too short
                    # rank = rank.replace(":", "")

        return rank

    def open_output_file(self, file_path):
        if sys.platform == "win32":
            os.startfile(file_path)
        elif sys.platform == "darwin":  # mac
            subprocess.call(["open", file_path])
        else:  # linux
            subprocess.call(["xdg-open", file_path])


if __name__ == '__main__':
    CONV = Converter()
    CONV.main()
