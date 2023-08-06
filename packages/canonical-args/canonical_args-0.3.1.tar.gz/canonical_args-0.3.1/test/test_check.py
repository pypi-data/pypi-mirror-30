import unittest

from canonical_args import check



class TestObj(object):
	pass

class TestCase_EvalSubtype(unittest.TestCase):

	def test_type_native(self):
		self.assertEqual(check.eval_subtype("str"), str)

	def test_type_list(self):
		self.assertEqual(check.eval_subtype("list([int, str, float])"),
						 [int, str, float])

	def test_type_dict(self):
		self.assertEqual(check.eval_subtype("dict({'thing1': int})"),
											{"thing1": int})

	def test_type_object(self):
		self.assertEqual(check.eval_subtype("test_check.TestObj"), TestObj)

	def test_type_choice(self):
		self.assertEqual(check.eval_subtype("one([int, float])"),
						 check.ChoiceOfOne([int, float]))

	def test_choice_of_one_with_object(self):
		self.assertEqual(
			check.eval_subtype("one([int, cls('test_check.TestObj')])"),
			check.ChoiceOfOne([int, TestObj]))

	def test_type_none(self):
		self.assertEqual(check.eval_subtype("NoneType"), type(None))

	def test_complex_type_with_none(self):
		self.assertEqual(check.eval_subtype("[int, str, NoneType]"),
						 [int, str, type(None)])


class TestCase_CheckSubtype(unittest.TestCase):

	def test_type_native_no_cast(self):
		self.assertEqual(check.check_subtype("testArg",
											 int,
											 10),
						 10)

	def test_type_native_no_cast_fail(self):
		try:
			check.check_subtype("testArg", int, "string")
		except AssertionError:
			# successful failure.... oxymoron
			pass
		else:
			self.fail("should have thrown AssertionError")

	def test_type_native_cast(self):
		self.assertEqual(check.check_subtype("testArg",
											 int,
											 "10",
											 should_cast=True),
						 10)

	def test_type_native_cast_fail(self):
		try:
			check.check_subtype("testArg", int, "string", should_cast=True)
		except ValueError:
			# successful failure
			pass
		else:
			self.fail("should have thrown ValueError")

	def test_type_choice_of_one(self):
		self.assertEqual(check.check_subtype("testArg",
											 check.ChoiceOfOne([int, float]),
											 58.1),
						 58.1)

	def test_type_choice_of_one_object(self):
		obj = TestObj()
		self.assertEqual(check.check_subtype("testArg",
											 check.ChoiceOfOne([int,
											 					TestObj]),
											 obj),
						 obj)

	def test_type_choice_of_one_fail(self):
		try:
			check.check_subtype("testArg",
								check.ChoiceOfOne([int, float]),
								"string")
		except AssertionError:
			pass
		else:
			self.fail("should have thrown AssertionError")

	def test_type_choice_of_one_with_none(self):
		check.check_subtype("testArg",
							check.ChoiceOfOne([int, float, type(None)]),
							None)


class TestCase_CheckValueWhitelist(unittest.TestCase):

	def test_value_whitelist(self):
		check.check_value_whitelist("testArg",
									["A", "B", "C"],
									"B")

	def test_value_whitelist_fail(self):
		try:
			check.check_value_whitelist("testArg",
										["A", "B", "C"],
										"X")
		except AssertionError:
			pass
		else:
			self.fail("should have thrown AssertionError")

class TestCase_CheckValueRange(unittest.TestCase):

	def test_value_range_int(self):
		check.check_value_range("testArg",
								"range(0, 50)",
								25)

	def test_value_range_int_fail(self):
		try:
			check.check_value_range("testArg",
									"range(0, 50)",
									51)
		except AssertionError:
			pass
		else:
			self.fail("should have thrown AssertionError")

	def test_value_range_float(self):
		check.check_value_range("testArg",
								"range(0, 50.5)",
								25.1)

	def test_value_range_float_fail(self):
		try:
			check.check_value_range("testArg",
									"range(0, 50.5)",
									50.6)
		except AssertionError:
			pass
		else:
			self.fail("should have thrown AssertionError")

	def test_value_range_upper_limit(self):
		check.check_value_range("testArg",
								"range(0, 10)",
								10)

class TestCase_CheckValueComparison(unittest.TestCase):

	def test_value_comparison_gt(self):
		check.check_value_comparison("testArg",
									 ">5",
									 10)

	def test_value_comparison_gt_fail(self):
		try:
			check.check_value_comparison("testArg",
										 ">5",
										 5)
		except AssertionError:
			pass
		else:
			self.fail("should have thrown AssertionError")

	def test_value_comparison_lt(self):
		check.check_value_comparison("testArg",
							 "<5",
							 0)

	def test_value_comparison_lt_fail(self):
		try:
			check.check_value_comparison("testArg",
										 "<5",
										 5)
		except AssertionError:
			pass
		else:
			self.fail("should have thrown AssertionError")

	def test_value_comparison_gte(self):
		check.check_value_comparison("testArg",
									 ">=5",
									 5)

	def test_value_comparison_gte_fail(self):
		try:
			check.check_value_comparison("testArg",
										 ">=5",
										 4)
		except AssertionError:
			pass
		else:
			self.fail("should have thrown AssertionError")

	def test_value_comparison_lte(self):
		check.check_value_comparison("testArg",
									 "<=5",
									 5)

	def test_value_comparison_lte_fail(self):
		try:
			check.check_value_comparison("testArg",
										 "<=5",
										 6)
		except AssertionError:
			pass
		else:
			self.fail("should have thrown AssertionError")

	def test_value_comparison_formatted(self):
		check.check_value_comparison(
			"testArg",
			"(>0||<0)&&!=10",
			-10)

	def test_value_comparison_formatted_fail(self):
		try:
			check.check_value_comparison(
				"testArg",
				"(>0||<0)&&!=10",
				10)
		except AssertionError:
			pass
		else:
			self.fail("should have thrown AssertionError")


class TestCase_CheckValue(unittest.TestCase):

	def test_check_value_choice_of_one(self):
		subname = "testArg"
		subtypes = check.ChoiceOfOne([int, float])
		subvalues = {
			"int": ">0",
			"float": "<0"
		}
		subarg = 1

		check.check_value(subname, subtypes, subvalues, subarg)

	def test_check_value_choice_of_one_fail(self):
		subname = "testArg"
		subtypes = check.ChoiceOfOne([int, float])
		subvalues = {
			"int": ">0",
			"float": "<0"
		}
		subarg = 50.3  # is float, but >0

		try:
			check.check_value(subname, subtypes, subvalues, subarg)
		except AssertionError:
			pass
		else:
			self.fail("should have thrown AssertionError")

	def test_check_value_choice_of_one_with_object(self):
		subname = "testArg"
		subtypes = check.ChoiceOfOne([int, TestObj])
		subvalues = {
			"int": ">0",
			"test_check.TestObj": None
		}
		subarg = TestObj()

		check.check_value(subname, subtypes, subvalues, subarg)

	def test_check_value_choice_of_one_with_none(self):
		subname = "testArg"
		subtypes = check.ChoiceOfOne([int, type(None)])
		subvalues = {
			"int": ">0",
			"NoneType": None
		}
		subarg = None

		check.check_value(subname, subtypes, subvalues, subarg)


