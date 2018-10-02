import unittest
import XMLParser
import CardCreator


class MyTestCase(unittest.TestCase):

    def test_Parser(self):
        self.assertEqual(1, 1)

    def testColors(self):
        class_under_test = CardCreator.Converter("any")
        class_under_test.load_colors()
        actual_colors = class_under_test.colors

        self.assertEqual(len(actual_colors), 10)

    def testLinkRemoval(self):
        class_under_test = XMLParser
        test_string = "Text<a href=bla></a>moreText"
        expected_string = "Text <i>link</i> moreText"
        actual_string = class_under_test.remove_link_tags(test_string)

        self.assertEqual(expected_string, actual_string)

    def testComplexLinkRemoval(self):
        test_string = "Text<a href=bla></a>moreText<a href=www.google.com></a>"
        expected_string = "Text <i>link</i> moreText <i>link</i> "
        actual_string = XMLParser.remove_link_tags(test_string)

        self.assertEqual(expected_string, actual_string)

    def testLinkRemovalWithOtherATag(self):
        test_string = "Text <a name=noHyperLink></a> moreText<a href=importantTag></a>"
        expected_string = "Text <a name=noHyperLink></a> moreText <i>link</i> "
        actual_string = XMLParser.remove_link_tags(test_string)

        self.assertEqual(expected_string, actual_string)

    def testLineRemoval(self):
        test_string = "A text \n with \n too \n many \n new \n lines"
        expected_result = "A text \n with \n too \n many "
        actual_string = XMLParser.remove_excessive_new_lines(test_string)

        self.assertEqual(actual_string, expected_result)


if __name__ == '__main__':
    unittest.main()
