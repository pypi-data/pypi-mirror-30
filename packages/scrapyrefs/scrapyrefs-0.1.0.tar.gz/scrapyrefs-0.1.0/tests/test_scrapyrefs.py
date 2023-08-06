import unittest

from scrapyrefs import scrapyrefs


class ScrapyrefsTest(unittest.TestCase):

    def test_stripspaces(self):

        result = scrapyrefs.strip_spaces('KAY , Martin , The Proper Place of Men and Machines in Language Translation , Palo Alto , Xerox Palo Alto Research Center [ en ligne ], 1980, <http://www.mt-archive.info/Kay-1980. pdf> ( page consultée le 10 janvier2013 ) .'.encode('utf-8'))

        expected = 'KAY, Martin, The Proper Place of Men and Machines in Language Translation, Palo Alto, Xerox Palo Alto Research Center [en ligne], 1980, <http://www.mt-archive.info/Kay-1980. pdf> (page consultée le 10 janvier2013).'.encode('utf-8')

        self.assertEqual(result, expected)
