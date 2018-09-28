import unittest
import XMLParser

class myTestCase(unittest.TestCase):

    def test_Parser(self):
        self.assertEqual(1,1)

    def testColors(self):
        classUnderTest = XMLParser.Converter()
        classUnderTest.load_colors()
        actualcolors = classUnderTest.colors

        self.assertEqual(len(actualcolors), 10)

    def testLinkRemoval(self):
        classUnderTest = XMLParser.Converter()
        testString = "Text<a href=bla></a>weitererText"
        expectedResult = "Text <i>link</i> weitererText"
        actualString = classUnderTest.remove_link_tags(testString)

        # self.assertEqual(actualString,expectedResult)
        self.assertEqual(expectedResult, actualString)

    def testComplexLinkRemoval(self):
        classUnderTest = XMLParser.Converter()
        testString = "Text<a href=bla></a>weitererText<a href=blubb></a>"
        expectedResult = "Text <i>link</i> weitererText <i>link</i> "
        actualString = classUnderTest.remove_link_tags(testString)

        self.assertEqual(expectedResult, actualString)

    def testLinkRemovalWithOtherATag(self):
        classUnderTest = XMLParser.Converter()
        testString = "Text <a name=noHyperLink></a> weitererText<a href=relevanterTagb></a>"
        expectedResult = "Text <a name=noHyperLink></a> weitererText <i>link</i> "
        actualString = classUnderTest.remove_link_tags(testString)

        self.assertEqual(expectedResult, actualString)

    def testLineRemoval(self):
        classUnderTest = XMLParser.Converter()
        testString = "A text \n with \n too \n many \n new \n lines"
        expectedResult = "A text \n with \n too \n many "
        actualString = classUnderTest.remove_excessive_new_lines(testString)

        self.assertEqual(actualString, expectedResult)

if __name__ == '__main__':
    unittest.main()