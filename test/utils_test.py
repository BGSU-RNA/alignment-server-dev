import utils as u
import unittest as ut

from werkzeug.exceptions import HTTPException


class ParseUnitsTest(ut.TestCase):
    def test_parse_single_unit(self):
        val = u.parse_units('2GOZ|1|A|A|3')
        ans = [tuple(["2GOZ|1|A|A|3", "2GOZ|1|A|A|3"])]
        self.assertEquals(ans, val)

    def test_parse_comma_list(self):
        val = u.parse_units('2GOZ|1|A|A|3,2GOZ|1|A|A|8')
        ans = [tuple(["2GOZ|1|A|A|3", "2GOZ|1|A|A|3"]), 
               tuple(["2GOZ|1|A|A|8", "2GOZ|1|A|A|8"])]
        self.assertEquals(ans, val)

    def test_parse_range(self):
        val = u.parse_units('2GOZ|1|A|A|3:2GOZ|1|A|A|5')
        ans = [tuple(['2GOZ|1|A|A|3', '2GOZ|1|A|A|5'])]
        self.assertEquals(ans, val)

    def test_parse_commas_and_colon(self):
        val = \
        u.parse_units('2GOZ|1|A|A|3:2GOZ|1|A|A|5,2GOZ|1|A|A|12,2GOZ|1|A|A|3:2GOZ|1|A|A|30')
        ans = [tuple(['2GOZ|1|A|A|3', '2GOZ|1|A|A|5']),
              tuple(['2GOZ|1|A|A|12', '2GOZ|1|A|A|12']),
               tuple(['2GOZ|1|A|A|3', '2GOZ|1|A|A|30'])]
        self.assertEquals(ans, val)

    def test_parse_too_many(self):
        self.assertRaises(HTTPException, u.parse_units, 
                          'a,a,a,2GOZ|1|A|A|3:2GOZ|1|A|A|5,2GOZ|1|A|A|12,2GOZ|1|A|A|3:2GOZ|1|A|A|30')

    def test_parse_invalid_range(self):
        self.assertRaises(HTTPException, u.parse_units, 
                          '2GOZ|1|A|A|3:2GOZ|1|A|A|5:2GOZ|1|A|A|12,2GOZ|1|A|A|3:2GOZ|1|A|A|30')
