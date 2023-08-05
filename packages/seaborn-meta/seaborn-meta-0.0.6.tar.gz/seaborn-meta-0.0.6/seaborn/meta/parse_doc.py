""" This module is to provide support for auto parsing function doc.
    It looks for the text in the doc string after :: but before :param
    It relies on the seaborn.callingfunction
    """
__author__ = 'Ben Christenson'
__date__ = "11/02/15"

from seaborn.meta.calling_function import function_doc
from datetime import datetime
import sys

if sys.version_info[0] == 2:
    STR = 'basestring'
else:
    STR = 'str'


def parse_doc_dict(text=None, split_character="::"):
    """
    Returns a dictionary of the parsed doc for 
    example the following would return {'a':'A','b':'B'} ::
        a:A
        b:B
    :param split_character:
    :param text: str of the text to parse, by default uses calling function doc
    :param split_character: str of the characters to split on in the doc string
    :return: dict
    """
    text = text or function_doc(2)
    text = text.split(split_character, 1)[-1]
    text = text.split(':param')[0].split(':return')[0]
    text = text.strip().split('\n')

    def clean(t): return t.split(':', 1)[0].strip(), t.split(':', 1)[1].strip()

    return dict(clean(line) for line in text)


def parse_doc_list(text=None, is_stripped=True, split_character="::"):
    """
    Returns a list of the parsed doc for 
    example the following would return ['a:A','b:'B] ::
        a:A
        b:B
    :param text: str of the text to parse, by default uses calling function doc
    :param is_stripped: bool if True each line will be stripped
    :param split_character: str of the characters to split on in the doc string
    :return: list
    """
    text = text or function_doc(2)
    text = text.split(split_character, 1)[-1]
    text = text.split(':param')[0].split(':return')[0]
    text = text.strip().split('\n')

    def clean(t): return is_stripped and t.strip() or t

    return [clean(line) for line in text]


def parse_doc_str(text=None, is_untabbed=True, is_stripped=True,
                  tab=None, split_character="::"):
    """
    Returns a str of the parsed doc for example 
    the following would return 'a:A\nb:B' ::
        a:A
        b:B
    :param text:            str of the text to parse, by 
                            default uses calling function doc
    :param is_untabbed:     bool if True will untab the text
    :param is_stripped:     bool if True will strip the text
    :param tab:             str of the tab to use when untabbing, 
                            by default it will self determine tab size
    :param split_character: str of the character to split the text on
    :return: dict
    """
    text = text or function_doc(2)
    text = text.split(split_character, 1)[-1]
    text = text.split(':param')[0].split(':return')[0]
    tab = is_untabbed and \
          (tab or text[:-1 * len(text.lstrip())].split('\n')[-1]) or ''
    text = is_stripped and text.strip() or text
    return text.replace('\n%s' % tab, '\n')


def parse_arg_types(text=None, is_return_included=False):
    """
    :param text:               str of the text to parse, by default 
                               uses calling function doc
    :param is_return_included: bool if True return will be return as well
    :return:                   dict of args and variable types
    """
    text = text or function_doc(2)
    if is_return_included:
        text = text.replace(':return:', ':param return:')
    ret = {}

    def evl(text_):
        try:
            return eval(text_)
        except Exception as e:
            return text_

    if ':param' in text:
        for param in text.split(':param ')[1:]:
            name, desc = param.split(':', 1)
            if desc.strip().startswith('list of '):
                ret[name.strip()] = (list, evl(desc.split()[2].replace('str', STR)))
            elif desc.strip().startswith('str timestamp'):
                ret[name.strip()] = datetime
            else:
                ret[name.strip()] = evl(desc.split(None, 1)[0].replace('str', STR))
    return ret

