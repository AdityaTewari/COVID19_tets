import math


def sort_condition(sort_list):
    return sort_list[1]


def sort_by_condition():
    """
    :return: conditions
    """
    random = [(2, 2), (3, 4), (4, 1), (1, 3)]
    random.sort(key=sort_condition)
    print(random)


def main():
    sort_by_condition()


if __name__ == '__main__':
    main()