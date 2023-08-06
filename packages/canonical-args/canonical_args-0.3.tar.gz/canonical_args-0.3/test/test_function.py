import unittest

from canonical_args import function


spec = {
	"args": [
		{"name": "arg1", "type": int, "values": None},
		{"name": "arg2", "type": float, "values": None}
	],
	"kwargs": {
		"kwarg1": {"type": int, "values": None}
	}
}
@function.arg_spec(spec, register=True)
def func1(*args, **kwargs):
	return args, kwargs

class TestCase_TestRegisterToFunc(unittest.TestCase):

	def test_get_func_scope(self):
		self.assertEqual(getattr(func1, function.FUNC_SPEC_VAR), spec)

	def test_get_func_spec_with_method(self):
		self.assertEqual(func1.get_spec(), spec)

class TestCase_TestArgSpecDecorator(unittest.TestCase):

	def test_fire_decorated_method(self):
		func1(1, 3.1, kwarg1=1)

	def test_fire_decorated_method_fail(self):
		try:
			func1(1, 3.1, kwarg1="string")  # bad kwarg1 type
		except AssertionError:
			pass
		else:
			self.fail("should have thrown AssertionError")
