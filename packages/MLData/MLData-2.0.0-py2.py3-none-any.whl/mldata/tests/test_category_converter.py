from mldata.lib.category_converter import CategoryConverter


def test_category_converter():
    converter = CategoryConverter(["good", "red", "good", "red", "good", "red", "good", "red"], [1, 0, 0, 0, 1, 0, 1, 1], 1)
    print(converter.convert())
