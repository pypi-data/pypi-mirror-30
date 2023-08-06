"""这是一个“nester.py"模块，定义了一个函数print_lol()，函数可以打印列表，其中包含了嵌套列表"""
def print_lol(the_list):
    """这个函数取一个位置参数the_list，是一个python列表，包括嵌套列表。这个函数可以将指定的列表中的每一个数据项递归的输出到屏幕上，每个数据项各占一行。"""
    for  each_item in the_list:
        if isinstance(each_item,list):
            print_lol(each_item)
        else:
                print(each_item)
