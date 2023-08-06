# -*- coding:utf-8 -*-

import re
from typing import Any

import pydash as py_


def exact_match(regexp: str, target: str):
    return bool(re.search(f'^{regexp}$', target))


def get_by_diff_key(d: dict, diff_key: str) -> Any:
    return py_.get(d, diff_key
                   .replace("root", "")
                   .replace("><", ".")
                   .replace(">", "")
                   .replace("<", "")
                   .replace("'", ""))
