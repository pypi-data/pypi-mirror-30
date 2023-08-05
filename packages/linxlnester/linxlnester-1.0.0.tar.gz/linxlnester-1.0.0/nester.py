"""这是一个学习模块，提供了一个名为print_lol模块，这个函数的
作用是打印列表，其中有可能包含嵌套列表
"""


def print_lol(the_list):
    """指定列表的每个数据项会（递归）输出到屏幕上，各数据项各行
    Arguments:
        the_list {list} -- 列表
    """
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item)
    else:
        print(each_item)
