import unittest

from canonical_args import structure



class TestObj(object):
	pass

class TestCase_CheckList(unittest.TestCase):

	def test_non_nested(self):
		names = ["arg1", "arg2", "arg3"]
		types = [int, float, str]
		values = [None, None, None]
		args = [1, 13.2, "thing"]

		structure.check_list(names, types, values, args)

	def test_non_nested_fail(self):
		names = ["arg1", "arg2", "arg3"]
		types = [int, float, str]
		values = [None, None, None]
		args = [1.1, 13.2, "thing"]

		try:
			structure.check_list(names, types, values, args)
		except AssertionError:
			pass
		else:
			self.fail("should have thrown AssertionError")

	def test_nested_list(self):
		names = ["arg1", "arg2", "arg3"]
		types = [int, float, [str, bool]]
		values = [None, None, [["thing1", "thing2"], None]]
		args = [1, 13.2, ["thing1", False]]

		structure.check_list(names, types, values, args)

	def test_nested_list_fail(self):
		names = ["arg1", "arg2", "arg3"]
		types = [int, float, [str, bool]]
		values = [None, None, [["thing1", "thing2"], None]]
		args = [1, 13.2, ["thing1"]]  # nested list is wrong size

		try:
			structure.check_list(names, types, values, args)
		except AssertionError:
			pass
		else:
			self.fail("should have thrown AssertionError")

	def test_nested_dict(self):
		names = ["arg1", "arg2", "arg3"]
		types = [int, float, dict]
		values = [None, None, {"a": {"type": int, "values": None},
							  "b": {"type": float, "values": None}}]
		args = [1, 13.2, {"a": 15, "b": 22.13}]

		structure.check_list(names, types, values, args)

	def test_nested_dict_fail(self):
		names = ["arg1", "arg2", "arg3"]
		types = [int, float, dict]
		values = [None, None, {"a": {"type": int, "values": None},
							  "b": {"type": float, "values": None}}]
		args = [1, 13.2, {"a": 15}]  # missing key "b"

		try:
			structure.check_list(names, types, values, args)
		except AssertionError:
			pass
		else:
			self.fail("should have thrown AssertionError")


class TestCase_CheckDict(unittest.TestCase):

	def test_non_nested(self):
		spec = {
			"kwarg1": {
				"type": int,
				"values": None
			},
			"kwarg2": {
				"type": float,
				"values": None
			}
		}
		kwargs = {"kwarg1": 1, "kwarg2": 33.1}

		structure.check_dict(spec, kwargs)

	def test_non_nested_fail(self):
		spec = {
			"kwarg1": {
				"type": int,
				"values": None
			},
			"kwarg2": {
				"type": float,
				"values": None
			}
		}
		kwargs = {"kwarg1": 1, "kwarg2": 3}  # kwarg2 has bad type

		try:
			structure.check_dict(spec, kwargs)
		except AssertionError:
			pass
		else:
			self.fail("should have thrown AssertionError")

	def test_non_nested_non_required(self):
		spec = {
			"kwarg1": {
				"type": int,
				"values": None
			},
			"kwarg2": {
				"type": float,
				"values": None,
				"required": False
			}
		}
		kwargs = {"kwarg1": 1}  # non required kwarg missing

		structure.check_dict(spec, kwargs)

	def test_non_nested_required(self):
		spec = {
			"kwarg1": {
				"type": int,
				"values": None
			},
			"kwarg2": {
				"type": float,
				"values": None,
				"required": True
			}
		}
		kwargs = {"kwarg1": 1, "kwarg2": 3.3}

		structure.check_dict(spec, kwargs)

	def test_non_nested_required_fail(self):
		spec = {
			"kwarg1": {
				"type": int,
				"values": None
			},
			"kwarg2": {
				"type": float,
				"values": None,
				"required": True
			}
		}
		kwargs = {"kwarg1": 1}  # missing required kwarg2

		try:
			structure.check_dict(spec, kwargs)
		except AssertionError:
			pass
		else:
			self.fail("should have thrown AssertionError")


	def test_nested_list(self):
		spec = {
			"kwarg1": {
				"type": int,
				"values": None
			},
			"kwarg2": {
				"type": [int, int, float],
				"values": [None, None, None]
			}
		}
		kwargs = {"kwarg1": 1, "kwarg2": [1, 2, 3.5]}

		structure.check_dict(spec, kwargs)

	def test_nested_list_fail(self):
		spec = {
			"kwarg1": {
				"type": int,
				"values": None
			},
			"kwarg2": {
				"type": [int, int, float],
				"values": [None, None, None]
			}
		}
		kwargs = {"kwarg1": 1, "kwarg2": [1, 2]}  # bad length

		try:
			structure.check_dict(spec, kwargs)
		except AssertionError:
			pass
		else:
			self.fail("should have thrown AssertionError")

	def test_nested_dict(self):
		spec = {
			"kwarg1": {
				"type": int,
				"values": None
			},
			"kwarg2": {
				"type": dict,
				"values": {
					"subkey1": {
						"type": str,
						"values": None
					},
					"subkey2": {
						"type": int,
						"values": None
					}
				}
			}
		}
		kwargs = {"kwarg1": 1, "kwarg2": {"subkey1": "a", "subkey2": 1}}

		structure.check_dict(spec, kwargs)

	def test_nested_dict_fail(self):
		spec = {
			"kwarg1": {
				"type": int,
				"values": None
			},
			"kwarg2": {
				"type": dict,
				"values": {
					"subkey1": {
						"type": str,
						"values": None
					},
					"subkey2": {
						"type": int,
						"values": None
					}
				}
			}
		}
		kwargs = {"kwarg1": 1, "kwarg2": {"subkey1": "a"}}  # missing key

		try:
			structure.check_dict(spec, kwargs)
		except AssertionError:
			pass
		else:
			self.fail("should have thrown AssertionError")

class TestCase_CheckArgs(unittest.TestCase):

	def test_check_args(self):
		spec = {
			"args": [
				{
					"name": "arg1",
					"type": int,
					"values": None
				}
			],
			"kwargs": {
				"kwarg1": {
					"type": float,
					"values": None
				}
			}
		}

		structure.check_args(spec, [1], {"kwarg1": 33.1})

	def test_check_args_fail(self):
		spec = {
			"args": [
				{
					"name": "arg1",
					"type": int,
					"values": None
				}
			],
			"kwargs": {
				"kwarg1": {
					"type": float,
					"values": None
				}
			}
		}

		try:
			structure.check_args(spec, [1], {"kwarg1": "string"})  # bad type
		except AssertionError:
			pass
		else:
			self.fail("should have thrown AssertionError")

	def test_check_args_with_eval(self):
		spec = {
			"args": [
				{
					"name": "arg1",
					"type": "int",
					"values": None
				}
			],
			"kwargs": {
				"kwarg1": {
					"type": "one([int, NoneType])",
					"values": {
						"int": ">0",
						"NoneType": None
					},
					"required": True
				}
			}
		}

		structure.check_args(spec, [1], {"kwarg1": None})


	def test_check_complex_args(self):
		from canonical_args.check import one, cls, NoneType, TypeType
		argspec = {
			"args": [
				{
					"name": "arg1",
					"type": "one([int, float, str])",
					"values": {
						"int": ">0&&!=5",
						"float": "<5.3||>7.8",
						"str": ["A", "B", "C", "X"]
					}
				},
				{
					"name": "arg2",
					"type": dict,
					"values": {
						"subkey1": {
							"type": cls('test_structure.TestObj'),
							"values": None,
							"required": True
						},
						"subkey2": {
							"type": TypeType,
							"values": [int, float],
							"required": False
						}
					}
				}
			],
			"kwargs": {
				"kwarg1": {
					"type": one([int, float, dict, NoneType]),
					"values": {
						"int": "!=100",
						"float": "range(0, 99)",
						"dict": {
							"subkey1": {
								"type": int,
								"values": ">=0&&!=10",
								"required": True
							},
							"subkey2": {
								"type": float,
								"values": None,
								"required": True
							}
						},
						"NoneType": None
					}
				},
				"kwarg2": {
					"type": one([int, NoneType]),
					"values": {
						"int": "(>10||<10)&&!=5",
						"NoneType": None
					}
				}
			}
		}

		structure.check_args(
			argspec,
			[0.113, {"subkey1": TestObj(), "subkey2": int}],
			{
				"kwarg1": {
					"subkey1": 5,
					"subkey2": 459.132
				},
				"kwarg2": None
			})