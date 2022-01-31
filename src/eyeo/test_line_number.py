from eyeo import current_line_number, __line__

def test_line_number():
    # NOTE if this function
    assert current_line_number() == 5
    assert __line__() == 6
    assert f"{__line__}" == "7"

if __name__ == "__main__":
    test_line_number()
