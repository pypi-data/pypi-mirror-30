'''这个模块包含一个叫做print_lol的函数，用来打印list'''


def print_lol(the_list, level):
    '''这个函数定义了参数the_list，代表了要打印的list。
    参数level，代表所打印字符串的层级。
    函数的功能是将数组中的每一个字符串打印成单独的一行，不同层级的字符串用空格区分'''
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item, level+1)
        else:
            for tab_stop in range(level):
                print('\t', end='')
            print(each_item)
