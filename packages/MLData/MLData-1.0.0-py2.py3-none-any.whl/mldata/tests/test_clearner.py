from mldata.lib.cleaner import Cleaner


def test_cleaner():
    cleaner = Cleaner([12, '', "null", 4, 6.0])
    print(cleaner.clean())
