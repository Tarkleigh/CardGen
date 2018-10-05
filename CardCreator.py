import html
import random

import reportlab.lib.pagesizes as sizes
import reportlab.lib.units as layout_units
import reportlab.pdfgen.canvas as pdf_canvas
from reportlab.lib import colors as reportlab_colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Frame
from reportlab.platypus import Paragraph
from reportlab.platypus import Table, TableStyle


class Converter:
    def __init__(self):
        self.start_x = 10
        self.start_y = 325
        self.frame_count = 1

        self.colors = []
        self.used_colors = {}
        self.styles = {}
        self.royal_blue = (0 / 256, 85 / 256, 164 / 256)

        self.UNASSIGNED = "Unassigned"
        self.LARGE_RANK_STYLE = "largeRankStyle"
        self.LARGE_RANK_STYLE_UNASSIGNED = "largeRankStyleUnassigned"
        self.FIRST_LINE = "firstLine"
        self.FIRST_LINE_UNASSIGNED = "firstLineUnassigned"

    def create_pdf(self, entries, output_path):
        self.load_colors()
        self.load_styles()

        canvas = pdf_canvas.Canvas(filename=output_path, bottomup=1,
                                   pagesize=sizes.landscape(sizes.A4))

        for entry in entries:
            assignee = entry["assignee"]
            rank = entry["rank"]

            card_color, first_line_style = self.get_first_line_style(assignee)
            rank_style = self.get_rank_style(rank, assignee, first_line_style)

            frame_content = []
            table_data = self.get_table_data(entry, first_line_style, rank_style)

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

    def get_first_line_style(self, assignee):
        first_line_style = self.FIRST_LINE
        if assignee == self.UNASSIGNED:
            card_color = self.royal_blue
            first_line_style = self.FIRST_LINE_UNASSIGNED
        else:
            card_color = self.get_card_color(assignee)
        return card_color, first_line_style

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

    def get_card_color(self, assignee):
        if assignee in self.used_colors:
            card_color = self.used_colors[assignee]
        else:
            card_color = random.choice(self.colors)
            self.used_colors[assignee] = card_color
            self.colors.remove(card_color)

        return card_color

    def get_table_data(self, entry, first_line_style, rank_style):
        priority_paragraph = Paragraph(entry["priority"], self.styles[first_line_style])
        summary_paragraph = Paragraph(entry["summary"], self.styles["summary"])
        description_label_paragraph = Paragraph("Description:", self.styles["label"])
        key_paragraph = Paragraph(entry["key"], self.styles["summary"])

        processor_label_paragraph = Paragraph("Processor:", self.styles["label"])
        rank_paragraph = Paragraph(entry["rank"], self.styles[rank_style])
        description_paragraph = self.get_description_paragraph(entry)
        processor_paragraph = self.get_processor_paragraph(entry["assignee"])

        data = [[rank_paragraph, priority_paragraph],
                [key_paragraph, summary_paragraph],
                [description_label_paragraph, description_paragraph],
                [processor_label_paragraph, processor_paragraph]]
        return data

    def get_processor_paragraph(self, assignee):
        # remove "Unassigned" so people can fill out the cards themselves
        if assignee == self.UNASSIGNED:
            assignee = ""
        if len(assignee) > 30:
            processor_paragraph = Paragraph(assignee, self.styles["smallProcessor"])
        else:
            processor_paragraph = Paragraph(assignee, self.styles["processor"])
        return processor_paragraph

    def get_description_paragraph(self, entry):
        description_string = entry.get("description", '')

        if len(description_string) > 160:
            description_string = description_string[0:161] + '...'

        try:
            description_paragraph = Paragraph(description_string, self.styles["description"])
        except ValueError:
            description_string = html.escape(description_string)
            description_paragraph = Paragraph(description_string, self.styles["description"])
        return description_paragraph

    def get_rank_style(self, rank, assignee, first_line_style):
        if len(rank) >= 7:
            if assignee == self.UNASSIGNED:
                rank_style = self.LARGE_RANK_STYLE_UNASSIGNED
            else:
                rank_style = self.LARGE_RANK_STYLE
        else:
            rank_style = first_line_style
        return rank_style

    def load_styles(self):
        first_line_style = ParagraphStyle(name=self.FIRST_LINE, fontName='Helvetica-Bold',
                                          fontSize=18, alignment=0)
        self.styles[self.FIRST_LINE] = first_line_style

        first_line_style_unassigned = ParagraphStyle(name=self.FIRST_LINE_UNASSIGNED,
                                                     fontName='Helvetica-Bold', fontSize=18,
                                                     alignment=0, textColor=reportlab_colors.white)
        self.styles[self.FIRST_LINE_UNASSIGNED] = first_line_style_unassigned

        large_rank_style = ParagraphStyle(name=self.LARGE_RANK_STYLE,
                                          fontName='Helvetica-Bold', fontSize=13,
                                          alignment=0)

        self.styles[self.LARGE_RANK_STYLE] = large_rank_style

        large_rank_style_unassigned = ParagraphStyle(name=self.LARGE_RANK_STYLE_UNASSIGNED,
                                                     fontName='Helvetica-Bold', fontSize=13,
                                                     alignment=0, textColor=reportlab_colors.white)

        self.styles[self.LARGE_RANK_STYLE_UNASSIGNED] = large_rank_style_unassigned

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
