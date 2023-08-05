import argparse


class ArgumentParserError(Exception): pass
class ExitError(Exception): pass

class ThrowingArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        raise ArgumentParserError(message)
    
    def exit(self, status=0, message=None):
        raise ExitError(message)

class PySparkParser(ThrowingArgumentParser):
    def __init__(self):
        super(PySparkParser,self).__init__(prog='%juspark')
        self.set_defaults(verbose=False)
        self.add_argument('--strict', action='store_true', help='fail on warnings')
        self.add_argument('--force', action='store_true', help='force re-initilisation of an existing spark context')
        self.add_argument('--silent', action='store_true', help='do not print any messages')
        self.add_argument('--verbose', action='store_true', help='print verbose debug output')
        self.add_argument('--profile', help='load one default arguments from one of the prededined profile files')

def parse_opts_from_conf(conf, sep = '='):
    #need do process it line by line
    def split_line(l):
        sep_first_index = l.find(sep)
        return (l, '') if sep_first_index<0 else (l[0:sep_first_index], l[(sep_first_index+1):])
    return dict(filter(lambda t: len(t[0])>0, map(split_line, conf)))

def parse_opts_from_cell(cell, sep=' '):
    return parse_opts_from_conf(cell.split('\n'), ' ')

def merge_dict(dd, *args):
    result = dd.copy()
    for d in args:
        result.update(d)
    return result