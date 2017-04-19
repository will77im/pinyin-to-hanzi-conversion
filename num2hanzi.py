# -*- coding: utf-8 -*-#
# http://www.gocalf.com/blog/number-to-chinese.html

CHINESE_NEGATIVE = u'负'
CHINESE_ZERO = u'零'
CHINESE_DIGITS = [u'', u'一', u'二', u'三', u'四', u'五', u'六', u'七', u'八', u'九']
CHINESE_UNITS = [u'', u'十', u'百', u'千']
CHINESE_GROUP_UNITS = [u'', u'万', u'亿', u'兆', u"京", u"垓", u"杼", u"穰", u"溝", u"澗", u"正", u"載", u"極"]

num2hanzi = {u'\uff10': u'零', u'\uff11': u'一', u'\uff12': u'二', u'\uff13': u'三', u'\uff14': u'四', u'\uff15': u'五',
             u'\uff16': u'六', u'\uff17': u'七', u'\uff18': u'八', u'\uff19': u'九', u'\u5e74': u'年'}


def _enumerate_digits(number):
    """
    :type number: int|long
    :rtype: collections.Iterable[int, int]
    """
    position = 0
    while number > 0:
        digit = number % 10
        number //= 10
        yield position, digit
        position += 1


def direct_match(number):
    return ''.join([num2hanzi[x] for x in list(number)])


def translate_number_to_chinese(number):
    """
    :type number: int|long
    :rtype: string
    """

    if not isinstance(number, int) and not isinstance(number, long):
        raise ValueError('number must be integer')

    if number == 0:
        return CHINESE_ZERO

    words = []

    if number < 0:
        words.append(CHINESE_NEGATIVE)
        number = -number

    group_is_zero = True
    need_zero = False
    for position, digit in reversed(list(_enumerate_digits(number))):
        unit = position % len(CHINESE_UNITS)
        group = position // len(CHINESE_UNITS)

        if digit != 0:
            if need_zero:
                words.append(CHINESE_ZERO)

            if digit != 1 or unit != 1 or not group_is_zero or (group == 0 and need_zero):
                words.append(CHINESE_DIGITS[digit])

            words.append(CHINESE_UNITS[unit])

        group_is_zero = group_is_zero and digit == 0

        if unit == 0 and not group_is_zero:
            words.append(CHINESE_GROUP_UNITS[group])

        need_zero = (digit == 0 and (unit != 0 or group_is_zero))

        if unit == 0:
            group_is_zero = True
    return ''.join(words)


def translate(number):
    percentage = False
    year = False

    if number[-1] == u'％':
        percentage = True
        number = number[:-1]

    elif number[-1] == u'年':
        year = True
        number = number[:-1]

    if u'\uff0e' in number:
        n = number.split(u'\uff0e')
        n0 = n[0]
        n1 = n[1]
        r0 = translate_number_to_chinese(int(n0))
        r1 = direct_match(n1)
        res = r0 + u'点' + r1
    else:
        if year:
            res = direct_match(number)
        else:
            res = translate_number_to_chinese(int(number))

    if percentage:
        return u'百分之' + res
    elif year:
        return res + u'年'
    else:
        return res
