import utils as u
import unittest as ut

from werkzeug.exceptions import HTTPException


class ParseUnitsTest(ut.TestCase):
    def test_parse_single_unit(self):
        val = u.split('2GOZ|1|A|A|3')
        ans = [tuple(["2GOZ|1|A|A|3", "2GOZ|1|A|A|3"])]
        self.assertEquals(ans, val)

    def test_parse_comma_list(self):
        val = u.split('2GOZ|1|A|A|3,2GOZ|1|A|A|8')
        ans = [tuple(["2GOZ|1|A|A|3", "2GOZ|1|A|A|3"]),
               tuple(["2GOZ|1|A|A|8", "2GOZ|1|A|A|8"])]
        self.assertEquals(ans, val)

    def test_parse_range(self):
        val = u.split('2GOZ|1|A|A|3:2GOZ|1|A|A|5')
        ans = [tuple(['2GOZ|1|A|A|3', '2GOZ|1|A|A|5'])]
        self.assertEquals(ans, val)

    def test_parse_commas_and_colon(self):
        val = \
            u.split('2GOZ|1|A|A|3:2GOZ|1|A|A|5,2GOZ|1|A|A|12,2GOZ|1|A|A|3:2GOZ|1|A|A|30')
        ans = [tuple(['2GOZ|1|A|A|3', '2GOZ|1|A|A|5']),
               tuple(['2GOZ|1|A|A|12', '2GOZ|1|A|A|12']),
               tuple(['2GOZ|1|A|A|3', '2GOZ|1|A|A|30'])]
        self.assertEquals(ans, val)

    def test_parse_too_many(self):
        self.assertRaises(HTTPException, u.split,
                          'a,a,a,2GOZ|1|A|A|3:2GOZ|1|A|A|5,2GOZ|1|A|A|12,2GOZ|1|A|A|3:2GOZ|1|A|A|30')

    def test_parse_missing_entry(self):
        self.assertRaises(HTTPException, u.split,
                          '2GOZ|1|A|A|3:2GOZ|1|A|A|5,,')

    def test_parse_missing_range(self):
        self.assertRaises(HTTPException, u.split,
                          '2GOZ|1|A|A|3:2GOZ|1|A|A|5,:')

    def test_parse_missing_end_of_range(self):
        self.assertRaises(HTTPException, u.split, '2GOZ|1|A|A|3:')

    def test_parse_missing_start_of_range(self):
        self.assertRaises(HTTPException, u.split, ':2GOZ|1|A|A|5')

    def test_parse_invalid_range(self):
        self.assertRaises(HTTPException, u.split,
                          '2GOZ|1|A|A|3:2GOZ|1|A|A|5:2GOZ|1|A|A|12,2GOZ|1|A|A|3:2GOZ|1|A|A|30')


class RangesTest(ut.TestCase):
    def simpilfy(self, result):
        pdb, model, ranges = result
        ranges = [(r[0]['chain'], r[0]['number'], r[1]['number']) for r in ranges]
        return pdb, model, ranges

    def test_can_generate_range_from_one_single(self):
        val = self.simpilfy(u.ranges({'units': '2GOZ|1|A|A|3'}))
        ans = ('2GOZ', 1, [('A', 3, 3)])
        self.assertEquals(ans, val)

    def test_can_generate_ranges_from_several_single(self):
        val = self.simpilfy(u.ranges({
            'units': '2GOZ|1|A|A|3,2GOZ|1|A|A|4,2GOZ|1|A|A|5'
        }))
        ans = ('2GOZ', 1, [('A', 3, 3), ('A', 4, 4), ('A', 5, 5)])
        self.assertEquals(ans, val)

    def test_can_generate_ranges_from_a_range(self):
        val = self.simpilfy(u.ranges({'units': '2GOZ|1|A|A|3:2GOZ|1|A|A|5'}))
        ans = ('2GOZ', 1, [('A', 3, 5)])
        self.assertEquals(ans, val)

    def test_can_generate_ranges_from_several_ranges(self):
        val = self.simpilfy(u.ranges({
            'units': '2GOZ|1|A|A|3:2GOZ|1|A|A|5,2GOZ|1|B|A|8:2GOZ|1|B|A|50'
        }))
        ans = ('2GOZ', 1, [('A', 3, 5), ('B', 8, 50)])
        self.assertEquals(ans, val)

    def test_requires_ranges_have_units(self):
        self.assertRaises(HTTPException, u.ranges, {})

    def test_requires_ranges_use_one_pdb(self):
        self.assertRaises(HTTPException, u.ranges, {
            'units': '2GOZ|1|A|A|3:2GOZ|1|A|A|5,2GOV|1|A|A|8:2GOZ|1|A|A|50'
        })

    def test_requires_ranges_use_one_model(self):
        self.assertRaises(HTTPException, u.ranges, {
            'units': '2GOZ|1|A|A|3:2GOZ|2|A|A|5,2GOZ|1|A|A|8:2GOZ|1|A|A|50'
        })

    def test_requires_each_pair_use_one_chain(self):
        self.assertRaises(HTTPException, u.ranges, {
            'units': '2GOZ|1|C|A|3:2GOZ|1|A|A|5,2GOZ|1|A|A|8:2GOZ|1|A|A|50'
        })


class ValidateRangesTest(ut.TestCase):
    def setUp(self):
        self.known = [
            {'pdb': '1S72', 'model_number': 1, 'chain_id': 'A'},
            {'pdb': '2AW7', 'model_number': 1, 'chain_id': 'A'},
            {'pdb': '2AW7', 'model_number': 3, 'chain_id': 'A'},
        ]

        self.ranges = [
            ({'pdb': '2AW7', 'model': 1, 'chain': 'A', 'number': 1,
              'insertion_code': None},
             {'pdb': '2AW7', 'model': 1, 'chain': 'A', 'number': 10,
              'insertion_code': None})
        ]

    def test_can_accept_valid_range(self):
        val = u.validate('2AW7', 1, self.ranges, self.known)
        self.assertTrue(val)

    def test_fails_with_bad_pdb(self):
        self.assertRaises(HTTPException, u.validate, '2AJ7', 1, self.ranges,
                          self.known)

    def test_fails_with_bad_model(self):
        self.assertRaises(HTTPException, u.validate, '2AW7', 2, self.ranges,
                          self.known)

    def test_fails_with_bad_chain(self):
        self.ranges[0][1]['chain'] = 'J'
        self.assertRaises(HTTPException, u.validate, '2AW7', 1, self.ranges,
                          self.known)

    def test_fails_with_backwards_residues(self):
        self.ranges[0] = (self.ranges[0][1], self.ranges[0][0])
        self.assertRaises(HTTPException, u.validate, '2AW7', 1, self.ranges,
                          self.known)


class TranslateTest(ut.TestCase):
    def setUp(self):
        self.no = lambda c: {}

        def basic(chain):
            return {(1, None): 2, (1, 'a'): 3, (2, None): 5}
        self.basic = basic

    def test_no_translation(self):
        ans = [({'chain': 'A', 'number': 1}, {'chain': 'A', 'number': 2})]
        val = u.translate(self.no, ans)
        self.assertEqual(ans, val)

    def test_basic_translation(self):
        ranges = [(
            {'chain': 'A', 'number': 1, 'insertion_code': 'a'},
            {'chain': 'A', 'number': 2}
        )]
        val = u.translate(self.basic, ranges)
        ans = [(
            {'chain': 'A', 'number': 3, 'insertion_code': 'a'},
            {'chain': 'A', 'number': 5}
        )]
        self.assertEqual(ans, val)

    def test_fails_for_too_large_a_range(self):
        self.assertRaises(HTTPException, u.translate, self.no, [
            ({'chain': 'A', 'number': 1}, {'chain': 'A', 'number': 200})
        ])

    def test_does_not_modify_given_data(self):
        ranges = [(
            {'chain': 'A', 'number': 1, 'insertion_code': 'a'},
            {'chain': 'A', 'number': 2}
        )]
        ranges2 = [(
            {'chain': 'A', 'number': 1, 'insertion_code': 'a'},
            {'chain': 'A', 'number': 2}
        )]
        u.translate(self.basic, ranges)
        self.assertEqual(ranges, ranges2)
