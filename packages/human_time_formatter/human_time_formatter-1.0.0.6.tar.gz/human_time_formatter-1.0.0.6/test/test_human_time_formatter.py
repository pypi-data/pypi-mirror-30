from builtins import zip
from builtins import range
from human_time_formatter import format_seconds, convert_ywdhms_to_seconds

def test_format_seconds_1():
    assert format_seconds(convert_ywdhms_to_seconds(0,0,0,0,0,10), 3) == '10s'

def test_format_seconds_2():
    assert format_seconds(convert_ywdhms_to_seconds(1,0,0,0,0,10), 3) == '1 year, 0 weeks'

def test_format_seconds_3():
    assert format_seconds(convert_ywdhms_to_seconds(0,1,0,0,0,10), 3) == '1 week, 0 days'

def test_format_seconds_4():
    assert format_seconds(convert_ywdhms_to_seconds(1,50,0,0,0,10), 3) == '1 year, 50 weeks'

def test_format_seconds_5():
    assert format_seconds(convert_ywdhms_to_seconds(1,50,0,0,0,10) ,8) == '1 year, 50 weeks, 0 days, 00:00m'

def test_format_seconds_6():
    assert format_seconds(convert_ywdhms_to_seconds(0,1,5,0,0,10), 3) == '1 week, 5 days'

def test_format_seconds_7():
    assert format_seconds(convert_ywdhms_to_seconds(0,0,0,0,1,10), 3) == '1:10s'

def test_format_seconds_8():
    assert format_seconds(convert_ywdhms_to_seconds(0,0,0,0,12,1.465) ,5) == '12:01.5s'

def test_format_seconds_9():
    assert format_seconds(convert_ywdhms_to_seconds(0,0,0,0,12,1.465) ,4) == '12:01s'

def test_format_seconds_10():
    assert format_seconds(convert_ywdhms_to_seconds(0,0,0,0,12,31.465) ,4) == '12:31s'

def test_format_seconds_11():
    assert format_seconds(convert_ywdhms_to_seconds(0,0,0,12,5,0), 6) == '12:05:00s'

def test_format_seconds_12():
    assert format_seconds(convert_ywdhms_to_seconds(143466,50,0,0,0,10), 8) == '143466 years, 50 weeks'

def test_format_seconds_13():
    assert format_seconds(convert_ywdhms_to_seconds(0,0,0,0,0,134e-11), 3) == '1.34ns'

def test_format_seconds_14():
    assert format_seconds(convert_ywdhms_to_seconds(0,0,0,0,0,134e-16), 3) == '13.4fs'

def test_format_seconds_15():
    assert format_seconds(convert_ywdhms_to_seconds(0,0,0,0,0,134e-40), 3) == '1.34e-38s'


def test_format_seconds_bulk():
    sec_list = [2.002**(i - 10) for i in range(0, 40, 2)]
    form_list = [format_seconds(i, ndigits=4) for i in sec_list]
    exp_list = ["966.9us",
                "3.875ms",
                "15.53ms",
                "62.25ms",
                "0.2495s",
                "1s",
                "4.008s",
                "16.06s",
                "1:04.4s",
                "4:18.1s",
                "17:14s",
                "1:09:05s",
                "4:36:55s",
                "18:29m",
                "3 days, 02:08m",
                "1 week, 5 days, 9h",
                "7 weeks, 0 days, 14h",
                "28 weeks, 2 days",
                "2 years, 9 weeks, 4 days",
                "8 years, 39 weeks, 2 days"]
    for seconds, formatted, expected in zip(sec_list, form_list, exp_list):
        msg = 'Failed on ndigits=4 with {} seconds; got {} but expected {}'
        assert formatted == expected, msg.format(seconds, formatted, expected)

if __name__ == "__main__":
    test_format_seconds_1()
    test_format_seconds_2()
    test_format_seconds_3()
    test_format_seconds_4()
    test_format_seconds_5()
    test_format_seconds_6()
    test_format_seconds_7()
    test_format_seconds_8()
    test_format_seconds_9()
    test_format_seconds_10()
    test_format_seconds_11()
    test_format_seconds_12()
    test_format_seconds_13()
    test_format_seconds_14()
    test_format_seconds_15()
    test_format_seconds_bulk()
