"""A replay receipt cannot be accepted from HTTP success alone."""
def single_effect(first, replay):
    keys = {'total', 'paid', 'payment_count', 'payment_sum', 'debt_payment_count', 'debt_payment_sum'}
    if not isinstance(first, dict) or not isinstance(replay, dict) or set(first) != keys or set(replay) != keys:
        raise ValueError('invalid collection effect receipt')
    if first != {'total': 100, 'paid': 20, 'payment_count': 1, 'payment_sum': 20,
                 'debt_payment_count': 1, 'debt_payment_sum': 20}:
        raise ValueError('first collection positive control missing')
    return first == replay
