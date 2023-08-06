# -*- coding: utf-8 -*-

''' SQL in F(unctions)

    udf_lib contains useful user-defined functions
'''


import re
import typeguard
import typing


###############################################################################
# Text Processing
###############################################################################


@typeguard.typechecked
def similar(string1: str, string2: str) -> bool:
    return list(re.findall('[a-z0-9]+', string1.lower())) == \
           list(re.findall('[a-z0-9]+', string2.lower()))


@typeguard.typechecked
def number(string: str) -> typing.Union[int, float, None]:
    for tmp in re.finditer('\d+(\.\d+)?', string):
        tmp = tmp.group(0)
        if '.' in tmp:
            return float(tmp)
        else:
            return int(tmp)
        break
