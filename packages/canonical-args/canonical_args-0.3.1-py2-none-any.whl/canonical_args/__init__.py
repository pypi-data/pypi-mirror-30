"""
Make top-level imports available.
"""
from __future__ import absolute_import

from .structure import check_args
from .function import arg_spec, register_spec



__all__ = ["check_args",
		   "arg_spec",
		   "register_spec"]
