from __future__ import print_function
import sys


#-----------------------------------------------------------------
# pycparser: __init__.py
#
# This package file exports some convenience functions for
# interacting with pycparser
#
# Eli Bendersky [http://eli.thegreenplace.net]
# Xeline Development Team [http://eli.thegreenplace.net]
# License: BSD
#-----------------------------------------------------------------
__all__ = ['c_lexer', 'c_parser', 'c_ast']
__version__ = '1.0'

#------------------------------------------------------------------------------
# pycparser: c-to-c.py
#
# Example of using pycparser.c_generator, serving as a simplistic translator
# from C to AST and back to C.
#
# Eli Bendersky [http://eli.thegreenplace.net]
# License: BSD
#------------------------------------------------------------------------------


# This is not required if you've installed pycparser into
# your site-packages/ with setup.py
#
sys.path.extend(['.', '..'])

from . import epl_generator


from subprocess import Popen, PIPE
from .c_parser import CParser


def preprocess_file(filename, cpp_path='cpp', cpp_args=''):
    """ Preprocess a file using cpp.
        filename:
            Name of the file you want to preprocess.
        cpp_path:
        cpp_args:
            Refer to the documentation of parse_file for the meaning of these
            arguments.
        When successful, returns the preprocessed file's contents.
        Errors from cpp will be printed out.
    """
    path_list = [cpp_path]
    if isinstance(cpp_args, list):
        path_list += cpp_args
    elif cpp_args != '':
        path_list += [cpp_args]
    path_list += [filename]

    try:
        # Note the use of universal_newlines to treat all newlines
        # as \n for Python's purpose
        #
        pipe = Popen(   path_list,
                        stdout=PIPE,
                        universal_newlines=True)
        text = pipe.communicate()[0]
    except OSError as e:
        raise RuntimeError("Unable to invoke 'cpp'.  " +
            'Make sure its path was passed correctly\n' +
            ('Original error: %s' % e))

    return text


def parse_file(filename, use_cpp=False, cpp_path='cpp', cpp_args='',
               parser=None):
    """ Parse a C file using pycparser.
        filename:
            Name of the file you want to parse.
        use_cpp:
            Set to True if you want to execute the C pre-processor
            on the file prior to parsing it.
        cpp_path:
            If use_cpp is True, this is the path to 'cpp' on your
            system. If no path is provided, it attempts to just
            execute 'cpp', so it must be in your PATH.
        cpp_args:
            If use_cpp is True, set this to the command line arguments strings
            to cpp. Be careful with quotes - it's best to pass a raw string
            (r'') here. For example:
            r'-I../utils/fake_libc_include'
            If several arguments are required, pass a list of strings.
        parser:
            Optional parser object to be used instead of the default CParser
        When successful, an AST is returned. ParseError can be
        thrown if the file doesn't parse successfully.
        Errors from cpp will be printed out.
    """
    if use_cpp:
        text = preprocess_file(filename, cpp_path, cpp_args)
    else:
        with open(filename, 'rU') as f:
            text = f.read()

    if parser is None:
        parser = CParser()
    return parser.parse(text, filename)


def translate_to_c(filename):
    """ Simply use the c_generator module to emit a parsed AST.
    """
    ast = parse_file(filename, use_cpp=False)
    generator = epl_generator.EPLGenerator()
    print(generator.visit(ast))


#------------------------------------------------------------------------------
def main():
    #_zz_test_translate()
    if len(sys.argv) > 1:
        translate_to_c(sys.argv[1])
    else:
        print("Please provide a filename as argument")
