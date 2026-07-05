from library import gen_random_int, create_string
from Models.Algorithms import BubbleSort

def test_gen_random_int():
    output = gen_random_int(10, 100, 9)
    assert output == [2, 6, 5, 6, 1, 2, 7, 8, 8, 7]

def test_bubble_sort():
    array = [10.3,3.8,8.4,47.1,1.0,0,-39.8,8.4,4.7,7.6,-6.5,-5.0]
    # sort() is a generator that mutates the array in place; exhaust it to sort.
    list(BubbleSort().sort(array))
    assert array == [-39.8, -6.5, -5.0, 0.0, 1.0, 3.8, 4.7, 7.6, 8.4, 8.4, 10.3, 47.1]

def test_create_string():
    array = [4, 0, 5, 9, 3, 1, 6, 8, 7, 2]
    output = create_string(array)
    assert output == "4, 0, 5, 9, 3, 1, 6, 8, 7, 2."
