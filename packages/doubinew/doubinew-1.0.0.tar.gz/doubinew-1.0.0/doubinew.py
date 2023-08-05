'''wanggengrun
2018.03.22'''
def print_lol(the_list):
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item)
        else:
            print(each_item)
            '''this is the standard way to include a mutiple-line
comment in your code'''
            '''注释也可用中文，小心无法显示'''
