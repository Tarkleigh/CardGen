import unittest
import xml_parser
import card_generator


class ParserTests(unittest.TestCase):

    def test_link_removal(self):
        class_under_test = xml_parser
        test_string = "Text<a href=bla></a>moreText"
        expected_string = "Text <i>link</i> moreText"
        actual_string = class_under_test.remove_link_tags(test_string)

        self.assertEqual(expected_string, actual_string)

    def test_complex_link_removal(self):
        test_string = "Text<a href=bla></a>moreText<a href=www.google.com></a>"
        expected_string = "Text <i>link</i> moreText <i>link</i> "
        actual_string = xml_parser.remove_link_tags(test_string)

        self.assertEqual(expected_string, actual_string)

    def test_link_removal_with_alternative_tag(self):
        test_string = "Text <a name=noHyperLink></a> moreText<a href=importantTag></a>"
        expected_string = "Text <a name=noHyperLink></a> moreText <i>link</i> "
        actual_string = xml_parser.remove_link_tags(test_string)

        self.assertEqual(expected_string, actual_string)

    def test_line_removal(self):
        test_string = "A text \n with \n too \n many \n new \n lines"
        expected_result = "A text \n with \n too \n many "
        actual_string = xml_parser.remove_excessive_new_lines(test_string)

        self.assertEqual(actual_string, expected_result)


class GeneratorTests(unittest.TestCase):

    def test_colors(self):
        class_under_test = card_generator.Generator()
        class_under_test.load_colors()
        actual_colors = class_under_test.colors

        self.assertEqual(len(actual_colors), 10)

    def test_rank_style_choice(self):
        class_under_test = card_generator.Generator()
        short_rank = "774"
        assignee = "Meyer, Max"
        first_line_style = "A first line style"

        rank_style = class_under_test.get_rank_style(short_rank, assignee, first_line_style)
        self.assertEqual(rank_style, first_line_style)

        # repeat with unassigned task, should not matter with a short rank
        rank_style = class_under_test.get_rank_style(short_rank, class_under_test.UNASSIGNED,
                                                     first_line_style)
        self.assertEqual(rank_style, first_line_style)

    def test_rank_style_choice_with_lexo_rank(self):
        class_under_test = card_generator.Generator()
        assignee = "Meyer, Max"
        lexo_rank = "0|hzzzz7:"
        first_line_style = "firstLine"

        rank_style = class_under_test.get_rank_style(lexo_rank, assignee, first_line_style)
        self.assertEqual(rank_style, class_under_test.LARGE_RANK_STYLE)

        # repeat with unassigned task
        rank_style = class_under_test.get_rank_style(lexo_rank, class_under_test.UNASSIGNED,
                                                     first_line_style)
        self.assertEqual(rank_style, class_under_test.LARGE_RANK_STYLE_UNASSIGNED)

    def test_color_choice_for_unassigned(self):
        class_under_test = card_generator.Generator()
        card_color, line_style = class_under_test.get_first_line_style(class_under_test.UNASSIGNED)
        self.assertEqual(card_color, class_under_test.ROYAL_BLUE)
        self.assertEqual(line_style, class_under_test.FIRST_LINE_UNASSIGNED)

    def test_get_color(self):
        class_under_test = card_generator.Generator()
        assignee = "Meyer, Max"

        # set color to hot pink
        hot_pink = (255 / 256, 110 / 256, 180 / 256)
        gold = (255 / 256, 236 / 256, 139 / 256)
        class_under_test.colors = [hot_pink]

        chosen_color = class_under_test.get_card_color(assignee)
        self.assertEqual(chosen_color, hot_pink)

        # re-set colors
        class_under_test.colors = [gold]
        chosen_color = class_under_test.get_card_color(assignee)
        self.assertEqual(chosen_color, hot_pink)


if __name__ == '__main__':
    unittest.main()
