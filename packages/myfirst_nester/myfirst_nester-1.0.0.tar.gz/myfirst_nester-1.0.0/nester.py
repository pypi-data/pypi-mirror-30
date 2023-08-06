'''这个模块包含一个叫做print_lol的函数，用来打印list'''
def print_lol(the_list):
    '''这个函数定义了参数the_list，代表了要打印的list。
    函数的功能是将数组中的每一个字符串打印成单独的一行。'''
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item)
        else:
            print(each_item)
