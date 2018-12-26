import pprint


def print_list(label, item_list):
    print '********************************'
    print label
    print '********************************'
    for item in item_list:
        pprint.pprint(item)
    print '\n'
