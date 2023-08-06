''' Functions to convert string case

History:
05-05-2015 - 1.0.0 - Stephen Funkhouser
    Created
'''
__version__ = '1.0.0'

import re


def camel_to_ashell_case(s):
    ''' convert camel case to A-Shell '''
    s1 = re.sub('(.)([A-Z][a-z]+)', r"\1'\2", s)
    return re.sub('([a-z0-9])([A-Z])', r"\1'\2", s1).lower()


def camel_to_snake_case(s):
    ''' convert camel case to snake case '''
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', s)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def upcase_first_letter(s, lower=False):
    ''' upper case first letter of string '''
    if lower:
        s = s.lower()
    return s[0].upper() + s[1:]
