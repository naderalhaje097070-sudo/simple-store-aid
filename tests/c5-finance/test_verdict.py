import unittest
from verdict import single_effect


class StoredReplay(unittest.TestCase):
    def setUp(self):
        self.first = {'total':100,'paid':20,'payment_count':1,'payment_sum':20,
                      'debt_payment_count':1,'debt_payment_sum':20}

    def test_single_committed_effect(self):
        self.assertTrue(single_effect(self.first, dict(self.first)))

    def test_duplicate_paid_and_cash_is_not_accepted(self):
        self.assertFalse(single_effect(self.first, {**self.first,'paid':40,'payment_count':2,
                                                  'payment_sum':40,'debt_payment_count':2,'debt_payment_sum':40}))

    def test_hidden_extra_payment_is_not_accepted(self):
        self.assertFalse(single_effect(self.first, {**self.first,'payment_count':2}))

    def test_http_success_without_stored_receipt_is_not_accepted(self):
        for value in [None,{}, {'success':True}]:
            with self.assertRaises(ValueError):
                single_effect(self.first, value)

    def test_missing_first_commit_positive_control(self):
        with self.assertRaises(ValueError):
            single_effect({**self.first,'paid':0}, self.first)


if __name__ == '__main__':
    unittest.main()
