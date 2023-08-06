"""This is the standard way to include
a multiple-line comment in your code"""


def print_lol(the_list):
    """This function need a program named the_list.
    The each item in the list will print in the screen"""
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item)
        else:
            print(each_item)

numbers = [1, 2, 3,[4, 5,[6, 7, 8]]]
print_lol(numbers)

