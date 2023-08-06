'''
this is the "nester_axin.py" module,and it provides one function
called print_nest() which prints lists that may or may not include nested lists
'''
def print_nest(test_list):
    for param in test_list:
        '''
        this function takes a positional argument called "test_list",which is
        any Python list(of,possibly,nested lists). Each data item in the provided
        list is (recursively) printed to the screen on its own line
        '''
        if isinstance(param,list):
            print_nest(param)
        else:
            print(param)
