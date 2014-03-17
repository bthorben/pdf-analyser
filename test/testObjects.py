import unittest
from objects import PdfObject
from StringIO import StringIO


class PdfObjectTest(unittest.TestCase):
    def test_string(self):
        self.assertEqual(self.parse(
                         "(Thorben Bochenek testet!)"),
                         "(Thorben Bochenek testet!)")

    def test_bstring(self):
        self.assertEqual(self.parse(
                         "<cafebabe>"),
                         "<cafebabe>")

    def test_name(self):
        self.assertEqual(self.parse(
                         "/Thorben"),
                         "/Thorben")

    def test_numberPositive(self):
        self.assertEqual(self.parse(
                         "25"),
                         "25")

    def test_numberNegativePointZero(self):
        self.assertEqual(self.parse(
                         "-7.0"),
                         "-7")

    def test_ref(self):
        self.assertEqual(self.parse(
                         "2 0 R"),
                         "2 0 R")

    def test_array(self):
        self.assertEqual(self.parse(
                         "[(BLABLABLA) <abf001cafebabe>]"),
                         "[(BLABLABLA)<abf001cafebabe>]")

    def test_dictEmpty(self):
        self.assertEqual(self.parse(
                         "<<>>"),
                         "<<\n>>\n")

    def test_dictNested(self):
        self.assertEqual(self.parse(
                         "<</Resources<<>>>>"),
                         "<<\n/Resources <<\n>>\n\n>>\n")

    def test_dictNamed(self):
        self.assertEqual(self.parse(
                         "<</Type/Page>>"),
                         "<<\n/Type /Page\n>>\n")

    def test_dictRef(self):
        self.assertEqual(self.parse(
                         "<</Parent 2 0 R>>"),
                         "<<\n/Parent 2 0 R\n>>\n")

    def parse(self, string):
        stream = StringIO(string)
        obj = PdfObject(stream)
        return str(obj)
