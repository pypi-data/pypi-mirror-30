'''wanggengrun
2018.03.22'''
def print_lol(the_list,indent=False,level=0):
    for each_item in the_list:
        if isinstance(each_item, list):
            print_lol(each_item,indent,level+1)
        else:
            if indent:
                for tab_stop in range(level):
                    print('\t',end='')
            print(each_item)
            '''this is the standard way to include a mutiple-line
comment in your code'''
            '''注释也可用中文，小心无法显示'''
