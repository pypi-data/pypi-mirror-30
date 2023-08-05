# -*- coding: utf-8 -*-

'''
Tests for ReCalc that do not involve tkinter.

testing_ReCalc.py
'''

import unittest
import doctest
import os
import math
import string

import numpy as np


class NonRepeatingList(object):
	'''
	A mutable list that doesn't have two of the same element in a row.

	>>> repr(NonRepeatingList(3, 3, 4))
	'NonRepeatingList(3, 4)'
	'''

	def __init__(self, *args):
		if len(args) > 0:
			self.items = [args[0]]
			for i in args:
				if i != self.items[-1]:
					self.items.append(i)
		else:
			self.items = []

	def __getitem__(self, index):
		return(self.items[index])

	def __delitem__(self, index):
		del self.items[index]
		if index != 0:
			if self.items[index] == self.items[index - 1]:
				del self.items[index]

	def __contains__(self, item):
		return(item in self.items)

	def __len__(self):
		return(len(self.items))

	def __repr__(self):
		return("NonRepeatingList(" + repr(self.items)[1:-1] + ")")

	def __str__(self):
		return(str(self.items))

	def __eq__(self, other):
		if isinstance(other, NonRepeatingList):
			if self.items == other.items:
				return(True)
		return(False)

	def append(self, *args):
		for item in args:
			if len(self.items) > 0:
				if self.items[-1] != item:
					self.items.append(item)
			else:
				self.items.append(item)

	def clear(self):
		self.items.clear()


import ReCalc as c


class TestCheckIfFloat(unittest.TestCase):
	'''
	Test that the check_if_float function works as expected.
	'''

	def test_float(self):
		'''
		Check that it works for floats.
		'''

		self.assertTrue(c.check_if_float(3.4))

	def test_int_type(self):
		'''
		Check that it works for ints.
		'''

		self.assertTrue(c.check_if_float(4))

	def test_string_type(self):
		'''
		Check that it works for floats as strings.
		'''

		self.assertTrue(c.check_if_float("3.4"))

	def test_word(self):
		'''
		Check that it returns false for words.
		'''

		self.assertFalse(c.check_if_float("hello"))

	def test_int_string(self):
		'''
		Check it works for ints as strings.
		'''

		self.assertTrue(c.check_if_float("2"))

	def test_mixed(self):
		self.assertFalse(c.check_if_float("sin(3.14)"))

	def test_parrentheses(self):
		self.assertFalse(c.check_if_float("(5)"))

	def test_list_type(self):
		self.assertFalse(c.check_if_float([2]))


class Files(unittest.TestCase):
	'''
	Check that require files and paths are present and exist.
	'''

	def test_main_path(self):
		'''
		Test that the path of the module actually exists.
		'''

		self.assertTrue(os.path.exists(c.calc_path))

	def test_picked_data(self):
		'''
		Check that the information file is present.
		'''

		self.assertTrue(
			os.path.isfile(
				os.path.join(c.calc_path, "ReCalc_info.txt")))

	def test_tkinter_icon(self):
		'''
		Check that the icon for the window is present.
		'''

		self.assertTrue(
			os.path.isfile(
				os.path.join(c.calc_path, "ReCalc_icon.ico")))


class SwitchDegreeMode(unittest.TestCase):
	'''
	Test the switch_degree_mode function works as expected.
	'''

	def setUp(self):
		'''
		Remember what the degree_mode started as.
		'''

		self.original_degree_mode = c.degree_mode

	def test_set_degree_mode(self):
		c.switch_degree_mode(2)
		self.assertEqual(c.degree_mode, 2)
		self.assertEqual(c.calc_info["degree_mode"], 2)

	def test_set_radian_mode(self):
		c.switch_degree_mode(0)
		self.assertEqual(c.degree_mode, 0)
		self.assertEqual(c.calc_info["degree_mode"], 0)

	def test_set_degree_mode_string(self):
		c.switch_degree_mode("degree")
		self.assertEqual(c.degree_mode, 2)
		self.assertEqual(c.calc_info["degree_mode"], 2)

	def test_set_radian_mode_string(self):
		c.switch_degree_mode("radian")
		self.assertEqual(c.degree_mode, 0)
		self.assertEqual(c.calc_info["degree_mode"], 0)

	def test_set_not_option(self):
		'''
		Check that switch_degree_mode throws an error if you pass it
		an invalid integer.
		'''

		with self.assertRaises(c.CalculatorError):
			c.switch_degree_mode(1)

	def test_set_to_random_word(self):
		'''
		Check that switch_degree_mode throws an error if you pass it
		an invalid string.
		'''

		with self.assertRaises(c.CalculatorError):
			c.switch_degree_mode("random")

	def tearDown(self):
		'''Set the degree_mode back to what it started as.'''

		c.switch_degree_mode(self.original_degree_mode)


class SwitchPolarCartesian(unittest.TestCase):
	'''
	Test switching between polar and Cartesian graphing modes works.
	'''

	def setUp(self):
		'''
		Remember what mode it started in.
		'''

		self.original_graphing_mode = c.polar_mode

	def test_set_polar(self):
		c.switch_polar_mode("polar")
		self.assertEqual(c.polar_mode, True)
		self.assertEqual(c.calc_info["polar_mode"], True)

	def test_set_cartesian(self):
		c.switch_polar_mode("Cartesian")
		self.assertEqual(c.polar_mode, False)
		self.assertEqual(c.calc_info["polar_mode"], False)

	def test_set_polar_boolean(self):
		c.switch_polar_mode(True)
		self.assertEqual(c.polar_mode, True)
		self.assertEqual(c.calc_info["polar_mode"], True)

	def test_set_cartesian_boolean(self):
		c.switch_polar_mode(False)
		self.assertEqual(c.polar_mode, False)
		self.assertEqual(c.calc_info["polar_mode"], False)

	def test_set_not_option(self):
		with self.assertRaises(c.CalculatorError):
			c.switch_polar_mode(4)

	def tearDown(self):
		c.switch_polar_mode(self.original_graphing_mode)


class FindMatch(unittest.TestCase):
	'''
	Test the find match function.
	'''

	def test_basic_functionality(self):
		self.assertEqual(
			c.find_match("(inside)outside"), ('(inside)', 'outside'))

	def test_extra_parentheses(self):
		self.assertEqual(
			c.find_match("((inside)))"), ('((inside))', ')'))

	def test_mismatched_parentheses_left(self):
		with self.assertRaises(c.CalculatorError):
			c.find_match("(word")

	def test_mismatched_parentheses_right(self):
		with self.assertRaises(c.CalculatorError):
			c.find_match("word)")


class BracketsFunction(unittest.TestCase):
	'''
	Test the brackets function.
	'''

	def test_matched_brackets(self):
		self.assertTrue(c.brackets(""))
		self.assertTrue(c.brackets("()"))
		self.assertTrue(c.brackets("(())"))
		self.assertTrue(c.brackets("(()())"))
		self.assertTrue(c.brackets("((word)(other)word)"))

	def test_unmatched_brackets(self):
		self.assertFalse(c.brackets("("))
		self.assertFalse(c.brackets(")"))
		self.assertFalse(c.brackets(")("))
		self.assertFalse(c.brackets("(()words"))


class Separate(unittest.TestCase):
	'''
	Test that the separate function works as expected.
	'''

	def test_split_no_parentheses(self):
		self.assertEqual(c.separate("2,4,5,6"), ("2", "4", "5", "6"))

	def test_split_parentheses(self):
		self.assertEqual(
			c.separate("3, 4, (5,6), 3"), ("3", " 4", " (5,6)", " 3"))

	def test_split_nested_parentheses(self):
		self.assertEqual(
			c.separate("1, (2, 3, (4, 5), 6), 7, (8), (9, 10)"),
			("1", " (2, 3, (4, 5), 6)", " 7", " (8)", " (9, 10)"))


class Constant(unittest.TestCase):
	'''
	Test that the constant function works as exprected.
	'''

	def test_all_the_constants(self):
		'''
		Test all the constants in the constant function.
		'''

		self.assertEqual(c.constant("pi"), math.pi)
		self.assertEqual(c.constant("e"), math.e)
		self.assertEqual(c.constant("phi"), (1 + 5 ** 0.5) / 2)
		self.assertEqual(c.constant("π"), math.pi)
		self.assertEqual(c.constant("ans"), c.ans)
		self.assertEqual(c.constant("answer"), c.ans)
		self.assertEqual(c.constant("tau"), math.tau)
		self.assertEqual(c.constant("τ"), math.tau)
		self.assertEqual(c.constant("φ"), (1 + 5 ** 0.5) / 2)

	def test_unknown_constant(self):
		'''
		Test that the constant function returns an error string if
		it gets passed an unknown constant.
		'''

		with self.assertRaises(c.CalculatorError):
			c.constant("pie")


class SolvingEquations(unittest.TestCase):
	'''
	Test solving equations works.
	'''

	def test_solve_with_no_equals_or_variable(self):
		self.assertEqual(c.solve_equations("x-5"), 5)

	def test_solve_with_no_equals(self):
		self.assertEqual(c.solve_equations("t-5 for t"), 5)

	def test_solve_with_no_variable(self):
		self.assertEqual(c.solve_equations("2*x = 4"), 2)

	def test_solve_with_everything(self):
		self.assertEqual(c.solve_equations("2*t = 4 for t"), 2)


class EvaluationFunction(unittest.TestCase):
	'''
	Test the evaluation function.
	'''

	def test_eval_without_variable(self):
		self.assertEqual(c.evaluate("x", "5"), "5")

	def test_eval_with_variable(self):
		self.assertEqual(c.evaluate("t", "5", var = "t"), "5")

	@unittest.expectedFailure
	def test_double_eval_function(self):
		'''
		Test nested evaluate statements.
		'''

		self.assertEqual(
			c.evaluate("eval t at x for t", "4"), "4")


class FindDerivative(unittest.TestCase):
	'''
	Test the find_derivative function.
	'''

	def test_find_basic_derivative(self):
		self.assertAlmostEqual(
			float(c.find_derivative("x^2", "3")), 6.0)

	def test_find_derivative_with_variable(self):
		self.assertAlmostEqual(
			float(c.find_derivative("t^2", "3", var = "t")), 6.0)

	@unittest.expectedFailure
	def test_double_derivative(self):
		'''
		Test nested derivative statements.
		'''

		self.assertAlmostEqual(
			float(c.find_derivative("x * derivative of t^2 at 3", "1")),
			6.0)


class IntegrateFunction(unittest.TestCase):
	'''
	Check that integration works as expected.
	'''

	def test_basic_integral(self):
		self.assertEqual(c.integrate_function("2*x", "x", "0", "3"), "9")

	def test_other_variables(self):
		'''
		Test integration works with respect to any lowercase variable.

		It will not work with 'I', 'E', 'S', 'N', 'C', 'O', or 'Q'
		because sympy uses those letters to represent other things.
		'''

		for i in string.ascii_lowercase:
			with self.subTest(i = i):
				self.assertEqual(
					c.integrate_function("2*%s" % i, i, "0", "3"),
					"9",
					msg = "Integrating with respect to %s failed" % i)

			self.assertEqual(
				c.integrate_function("2*A", "A", "0", "3"), "9")

	def test_integrate_at_expression(self):
		'''
		Test that integrate can integrate from a point that is not
		a single number.
		'''

		self.assertEqual(
			c.integrate_function("2*x", "x", "0", "1+2"), "9")


class CombinationsAndPermutations(unittest.TestCase):
	'''
	Test that combinations_and_permutations works as expected.
	'''

	def test_basic_combination_choose_notation(self):
		self.assertEqual(
			c.combinations_and_permutations("choose", "C", "5", "2"),
			"10.0")

	def test_basic_permutaion_choose_notation(self):
		self.assertEqual(
			c.combinations_and_permutations("choose", "P", "5", "2"),
			"20.0")

	def test_basic_combination_func_notation(self):
		self.assertEqual(
			c.combinations_and_permutations("func", "C", "(5,2)"),
			"10.0")

	def test_basic_permutaion_func_notation(self):
		self.assertEqual(
			c.combinations_and_permutations("func", "P", "(5,2)"),
			"20.0")

	def test_nested_combinations(self):
		self.assertEqual(
			c.combinations_and_permutations("func", "C", "(5,C(2,1))"),
			"10.0")

	def test_nested_permutations(self):
		self.assertEqual(
			c.combinations_and_permutations("func", "P", "(5,P(2,1))"),
			"20.0")

	def test_nested_mixed(self):
		self.assertEqual(
			c.combinations_and_permutations("func", "P", "(C(5,1),P(2,1))"),
			"20.0")

	def test_nested_mixed2(self):
		self.assertEqual(
			c.combinations_and_permutations("func", "C", "(C(5,1),P(2,1))"),
			"10.0")

	def test_choose_notation_needs_four_arguments(self):
		with self.assertRaises(c.CalculatorError):
			c.combinations_and_permutations("choose", "C", "(5,2)")

	def test_function_notation_needs_only_three_arguments(self):
		with self.assertRaises(c.CalculatorError):
			c.combinations_and_permutations("func", "C", "5", m = "2")

	def test_raises_errors_for_not_c_or_p_choose_notaion(self):
		with self.assertRaises(c.CalculatorError):
			c.combinations_and_permutations("choose", "R", "5", "2")

	def test_raises_errors_for_not_c_or_p_func_notaion(self):
		with self.assertRaises(c.CalculatorError):
			c.combinations_and_permutations("func", "R", "(5, 2)")


class StatisticsFunctions(unittest.TestCase):
	'''
	Test that statistics_functions works as expected.
	'''

	def test_all_basic_statistics(self):
		'''Test basic usage of statistics functions.'''

		self.assertEqual(
			c.statistics_functions("mean", "(4, 6, 39, 2, 11)"),
			"12.4")
		self.assertEqual(
			c.statistics_functions("ave", "(4, 6, 39, 2, 11)"),
			"12.4")
		self.assertEqual(
			c.statistics_functions("mean", "(4, 6, 39, 2, 11)"),
			"12.4")
		self.assertEqual(
			c.statistics_functions("median", "(1, 2, 3, 1, 7)"),
			"2")
		self.assertEqual(
			c.statistics_functions("mode", "(1, 2, 3, 1, 7)"),
			"1")
		self.assertEqual(
			c.statistics_functions("min", "(3, 6, 11, -7, -1, 55)"),
			"-7")
		self.assertEqual(
			c.statistics_functions("max", "(3, 6, 11, -7, -1, 55)"),
			"55")
		self.assertAlmostEqual(
			float(c.statistics_functions("stdev", "(3, 4, 4, 6, 8)")),
			2.0)

	def test_nested_stats_functions(self):
		self.assertEqual(
			c.statistics_functions("mean", "(1, 2, mean(1, 3, 5))"),
			"2")

	def test_not_defined_functions(self):
		'''
		Test that statistics_functions returns an error string
		when you pass it an undefined function.
		'''

		with self.assertRaises(c.CalculatorError):
			c.statistics_functions("sin", "(pi)")


class SingleArgumentFunction(unittest.TestCase):
	'''
	Test the single_argument function.
	'''

	def setUp(self):
		self.mode = c.degree_mode
		c.switch_degree_mode(0)

	def test_basic_trig_functions(self):
		self.assertAlmostEqual(
			float(c.single_argument("sin", "(pi/6)")),
			0.5)
		self.assertAlmostEqual(
			float(c.single_argument("cos", "(pi/3)")),
			0.5)
		self.assertAlmostEqual(
			float(c.single_argument("tan", "(pi/4)")),
			1.0)
		self.assertAlmostEqual(
			float(c.single_argument("sec", "(pi/3)")),
			2.0)
		self.assertAlmostEqual(
			float(c.single_argument("csc", "(pi/6)")),
			2.0)
		self.assertAlmostEqual(
			float(c.single_argument("cot", "(pi/4)")),
			1.0)

	def test_hyperbolic_trig_functions(self):
		self.assertAlmostEqual(
			float(c.single_argument("sinh", "(1)")),
			(math.e ** 2 - 1) / (2 * math.e))
		self.assertAlmostEqual(
			float(c.single_argument("cosh", "(1)")),
			(math.e ** 2 + 1) / (2 * math.e))
		self.assertAlmostEqual(
			float(c.single_argument("tanh", "(1)")),
			(math.e ** 2 - 1) / (math.e ** 2 + 1))
		self.assertAlmostEqual(
			float(c.single_argument("csch", "(1)")),
			(2 * math.e) / (math.e ** 2 - 1))
		self.assertAlmostEqual(
			float(c.single_argument("sech", "(1)")),
			(2 * math.e) / (math.e ** 2 + 1))
		self.assertAlmostEqual(
			float(c.single_argument("coth", "(1)")),
			(math.e ** 2 + 1) / (math.e ** 2 - 1))

	def test_inverse_trig_functions(self):
		self.assertAlmostEqual(
			float(c.single_argument("asin", "(.5)")),
			math.pi / 6)
		self.assertAlmostEqual(
			float(c.single_argument("acos", "(.5)")),
			math.pi / 3)
		self.assertAlmostEqual(
			float(c.single_argument("atan", "(3 ** .5)")),
			math.pi / 3)
		self.assertAlmostEqual(
			float(c.single_argument("asec", "(2)")),
			math.pi / 3)
		self.assertAlmostEqual(
			float(c.single_argument("acsc", "(2)")),
			math.pi / 6)
		self.assertAlmostEqual(
			float(c.single_argument("acot", "(3 ** .5)")),
			math.pi / 6)

	def test_inverse_hyperbolic_functions(self):
		'''Test basic usage of inverse hyperbolic trig functions.'''

		self.assertAlmostEqual(
			float(c.single_argument(
				"asinh",
				"(((e ** 2) - 1) / (2 * e))")),
			1)
		self.assertAlmostEqual(
			float(c.single_argument(
				"acosh",
				"((e ** 2 + 1) / (2 * e))")),
			1)
		self.assertAlmostEqual(
			float(c.single_argument(
				"atanh",
				"((e ** 2 - 1) / (e ** 2 + 1))")),
			1)
		self.assertAlmostEqual(
			float(c.single_argument(
				"acsch",
				"((2 * e) / (e ** 2 - 1))")),
			1)
		self.assertAlmostEqual(
			float(c.single_argument(
				"asech",
				"((2 * e) / (e ** 2 + 1))")),
			1)
		self.assertAlmostEqual(
			float(c.single_argument(
				"acoth",
				"((e ** 2 + 1) / (e ** 2 - 1))")),
			1)

	def test_archaic_trig_functions(self):
		'''Test basic usage of old mostly abandoned trig functions.'''

		self.assertAlmostEqual(
			float(c.single_argument("versin", "(pi/3)")),
			.5)
		self.assertAlmostEqual(
			float(c.single_argument("vercosin", "(pi/3)")),
			1.5)
		self.assertAlmostEqual(
			float(c.single_argument("coversin", "(pi/6)")),
			.5)
		self.assertAlmostEqual(
			float(c.single_argument("covercosin", "(pi/6)")),
			1.5)
		self.assertAlmostEqual(
			float(c.single_argument("haversin", "(pi/3)")),
			.25)
		self.assertAlmostEqual(
			float(c.single_argument("havercosin", "(pi/3)")),
			.75)
		self.assertAlmostEqual(
			float(c.single_argument("hacoversin", "(pi/6)")),
			.25)
		self.assertAlmostEqual(
			float(c.single_argument("hacovercosin", "(pi/6)")),
			.75)
		self.assertAlmostEqual(
			float(c.single_argument("exsec", "(0)")),
			0)
		self.assertAlmostEqual(
			float(c.single_argument("excsc", "(pi/2)")),
			0)

	def test_other_functions(self):
		'''Test basic usage of single argument functions that
		are not in anyway trig functions.'''

		self.assertEqual(
			c.single_argument("abs", "(-1)"),
			"1")
		self.assertEqual(
			c.single_argument("abs", "(3)"),
			"3")
		self.assertEqual(
			c.single_argument("ceil", "(.5)"),
			"1")
		self.assertEqual(
			c.single_argument("ceil", "(-1.5)"),
			"-1")
		self.assertEqual(
			c.single_argument("floor", "(4.8)"),
			"4")
		self.assertEqual(
			c.single_argument("floor", "(-4.8)"),
			"-5")
		self.assertAlmostEqual(
			float(c.single_argument("erf", "(e)")),
			0.9998790689599)

	def test_trig_functions_with_degree_symbol(self):
		self.assertAlmostEqual(
			float(c.single_argument("sin", "(30°)")),
			0.5)
		self.assertAlmostEqual(
			float(c.single_argument("cos", "(60°)")),
			0.5)
		self.assertAlmostEqual(
			float(c.single_argument("tan", "(45°)")),
			1.0)
		self.assertAlmostEqual(
			float(c.single_argument("sec", "(60°)")),
			2.0)
		self.assertAlmostEqual(
			float(c.single_argument("csc", "(30°)")),
			2.0)
		self.assertAlmostEqual(
			float(c.single_argument("cot", "(45°)")),
			1.0)

	def test_nested_trig_functions(self):
		self.assertAlmostEqual(
			float(c.single_argument("sin", "(asin(.56))")),
			.56)
		self.assertAlmostEqual(
			float(c.single_argument("cos", "(sin(0))")),
			1)
		self.assertAlmostEqual(
			float(c.single_argument("sin", "(cos(pi/2))")),
			0)
		self.assertAlmostEqual(
			float(c.single_argument("sin", "(asin(.12))")),
			.12)
		self.assertAlmostEqual(
			float(c.single_argument("asin", "(sin(1.33))")),
			1.33)

	def tearDown(self):
		c.switch_degree_mode(self.mode)


class InverseFunctionsDegreeMode(unittest.TestCase):
	'''
	Test inverse hyperbolic and trig function while in degree mode.
	'''

	def setUp(self):
		'''
		Remember what mode it started in. Then switch to degree mode.
		'''

		self.mode = c.degree_mode
		c.switch_degree_mode(2)

	def test_inverse_trig_functions_degree_mode(self):
		self.assertAlmostEqual(
			float(c.single_argument("asin", "(.5)")),
			30)
		self.assertAlmostEqual(
			float(c.single_argument("acos", "(.5)")),
			60)
		self.assertAlmostEqual(
			float(c.single_argument("atan", "(1)")),
			45)
		self.assertAlmostEqual(
			float(c.single_argument("asec", "(2)")),
			60)
		self.assertAlmostEqual(
			float(c.single_argument("acsc", "(2)")),
			30)
		self.assertAlmostEqual(
			float(c.single_argument("acot", "(1)")),
			45)

	def test_inverse_hyperbolic_functions_degree_mode(self):
		self.assertAlmostEqual(
			float(c.single_argument(
				"asinh", "(0.5478534738880397)")),
			30)
		self.assertAlmostEqual(
			float(c.single_argument(
				"acosh", "(1.600286857702386)")),
			60)
		self.assertAlmostEqual(
			float(c.single_argument(
				"atanh", "(0.6557942026326724)")),
			45)
		self.assertAlmostEqual(
			float(c.single_argument(
				"asech", "(0.6248879662960872)")),
			60)
		self.assertAlmostEqual(
			float(c.single_argument(
				"acsch", "(1.8253055746879534)")),
			30)
		self.assertAlmostEqual(
			float(c.single_argument(
				"acoth", "(1.5248686188220641)")),
			45)

	def tearDown(self):
		'''
		Go back to what mode it started in.
		'''

		c.switch_degree_mode(self.mode)


class GammaAndFactorial(unittest.TestCase):
	'''
	Test the gamma and factorial functions.
	'''

	def test_gamma(self):
		for i in np.arange(1.0, 10.0, .5):
			with self.subTest(i = i):
				self.assertAlmostEqual(
					float(c.gamma("(%s)" % i)), math.gamma(i))

	def test_factorial(self):
		for i in range(10):
			with self.subTest(i = i):
				self.assertEqual(
					c.factorial(str(i)), math.gamma(i + 1))


class Logarithm(unittest.TestCase):
	'''
	Test the logarithm function.
	'''

	def test_log(self):
		'''
		Test logarithm with base 3.
		'''

		self.assertEqual(c.logarithm("(9, 3)"), "2.0")

	def test_log2(self):
		'''
		Test logarithm with base 2.
		'''

		self.assertEqual(c.logarithm("(8, 2)"), "3.0")

	def test_log10(self):
		'''
		Test logarithm with base 10.
		'''

		self.assertEqual(c.logarithm("(.1, 10)"), "-1.0")

	def test_ln(self):
		'''
		Test logarithm with one argument.
		'''

		self.assertEqual(c.logarithm("(e^2)"), "2.0")

	def test_nested_logs(self):
		'''
		Test logarithm with another log as an argument.
		'''

		self.assertEqual(c.logarithm("(27, log(8, 2))"), "3.0")


class Modulus(unittest.TestCase):
	'''
	Test the modulus function.
	'''

	def test_modulus(self):
		self.assertEqual(c.modulus("(7, 4)"), "3.0")
		self.assertEqual(c.modulus("(9, 4)"), "1.0")
		self.assertEqual(c.modulus("(9, 3)"), "0.0")
		self.assertEqual(c.modulus("(5, 2)"), "1.0")

	def test_nested_modulus(self):
		'''
		Test modulus with another modulus as an argument.
		'''

		self.assertEqual(c.modulus("(11, mod(3, 4))"), "2.0")


class AbsoluteValue(unittest.TestCase):
	'''
	Test the absolute_value function.
	'''

	def test_basic(self):
		self.assertEqual(c.abs_value("|-1|"), "1.0")

	def test_expression(self):
		self.assertEqual(c.abs_value("|4-9|"), "5.0")

	def test_starts_with_negative(self):
		self.assertEqual(c.abs_value("|-1*3|"), "3.0")

	def test_nested(self):
		self.assertEqual(c.abs_value("||5-6||"), "|1.0|")

	def test_nested_negative(self):
		self.assertEqual(c.abs_value("|-1*|2-6||"), "|-1*4.0|")

	def test_subtract_abs_val(self):
		self.assertEqual(c.abs_value("|3-|1-7||"), "|3-6.0|")

	def test_double_nested(self):
		self.assertEqual(c.abs_value("|1-|3+|-4|||"), "|1-|3+4.0||")

	def test_parts_outside_abs_value(self):
		self.assertEqual(c.abs_value("4+|-3|"), "4+3.0")

	def test_multiply_abs_value(self):
		self.assertEqual(c.abs_value("2*|3-1|"), "2*2.0")

	def test_two_separate_abs_values(self):
		self.assertEqual(c.abs_value("|3-2|+|-1*3|"), "1.0+|-1*3|")

	def test_unmatched_pipes(self):
		with self.assertRaises(c.CalculatorError):
			c.abs_value("|1")


class Comma(unittest.TestCase):
	'''
	Test the comma function.
	'''

	def test_remove_commas(self):
		self.assertEqual(c.comma("456", "345"), "456345")
		self.assertEqual(c.comma("6", "345"), "6345")
		self.assertEqual(c.comma("21", "345.3333"), "21345.3333")
		self.assertEqual(c.comma("45", "345."), "45345.")

	def test_returns_error_string_if_wrong(self):
		with self.assertRaises(c.CalculatorError):
			c.comma("21", "32")
		with self.assertRaises(c.CalculatorError):
			c.comma("21", "3234")
		with self.assertRaises(c.CalculatorError):
			c.comma("21", "32.123")
		with self.assertRaises(c.CalculatorError):
			c.comma("21", "")


class Regex(unittest.TestCase):
	'''
	Test that the regular expression match the correct strings in the
	correct way.
	'''

	def test_reg_num_matches(self):
		self.assertRegex("1", "^" + c.reg_num + "$")
		self.assertRegex("2.0", "^" + c.reg_num + "$")
		self.assertRegex("4.6", "^" + c.reg_num + "$")
		self.assertRegex("30", "^" + c.reg_num + "$")
		self.assertRegex("-5", "^" + c.reg_num + "$")
		self.assertRegex("-3.0", "^" + c.reg_num + "$")
		self.assertRegex("-5.1", "^" + c.reg_num + "$")
		self.assertRegex("-54", "^" + c.reg_num + "$")
		self.assertRegex("-34.8", "^" + c.reg_num + "$")
		self.assertRegex("-94.889", "^" + c.reg_num + "$")
		self.assertRegex("954.189", "^" + c.reg_num + "$")
		self.assertRegex(".189", "^" + c.reg_num + "$")
		self.assertRegex("954.", "^" + c.reg_num + "$")
		self.assertRegex("-54.", "^" + c.reg_num + "$")
		self.assertRegex("-.3", "^" + c.reg_num + "$")

	def test_reg_num_does_not_match(self):
		self.assertNotRegex("text", "^" + c.reg_num + "$")
		self.assertNotRegex("1 . 2", "^" + c.reg_num + "$")
		self.assertNotRegex("1 .2", "^" + c.reg_num + "$")
		self.assertNotRegex("- 1.2", "^" + c.reg_num + "$")
		self.assertNotRegex("+ 1.2", "^" + c.reg_num + "$")

	def test_command_comp(self):
		'''
		Test that all the commands get matched by the regular
		expression.
		'''

		self.assertRegex("history", c.regular_expr["command_comp"])
		self.assertRegex("History", c.regular_expr["command_comp"])
		self.assertRegex("quit", c.regular_expr["command_comp"])
		self.assertRegex("Quit", c.regular_expr["command_comp"])
		self.assertRegex("exit", c.regular_expr["command_comp"])
		self.assertRegex("Exit", c.regular_expr["command_comp"])
		self.assertRegex("degree mode", c.regular_expr["command_comp"])
		self.assertRegex("Degree mode", c.regular_expr["command_comp"])
		self.assertRegex("degree Mode", c.regular_expr["command_comp"])
		self.assertRegex("Degree Mode", c.regular_expr["command_comp"])
		self.assertRegex("radian mode", c.regular_expr["command_comp"])
		self.assertRegex("Radian mode", c.regular_expr["command_comp"])
		self.assertRegex("radian Mode", c.regular_expr["command_comp"])
		self.assertRegex("Radian Mode", c.regular_expr["command_comp"])
		self.assertRegex("", c.regular_expr["command_comp"])

	def test_const_comp(self):
		'''
		Test that all the constants get matched by the regular
		expression.
		'''

		self.assertRegex("pi", c.regular_expr["const_comp"])
		self.assertRegex("π", c.regular_expr["const_comp"])
		self.assertRegex("e", c.regular_expr["const_comp"])
		self.assertRegex("ans", c.regular_expr["const_comp"])
		self.assertRegex("answer", c.regular_expr["const_comp"])
		self.assertRegex("e", c.regular_expr["const_comp"])
		self.assertRegex("tau", c.regular_expr["const_comp"])
		self.assertRegex("τ", c.regular_expr["const_comp"])
		self.assertRegex("phi", c.regular_expr["const_comp"])
		self.assertRegex("φ", c.regular_expr["const_comp"])

	def test_const_comp_not_match_e_in_a_word(self):
		'''
		Test that the constant e isn't matched if it is surrounded
		by other letters.
		'''

		self.assertNotRegex("ae", c.regular_expr["const_comp"])
		self.assertNotRegex("hare", c.regular_expr["const_comp"])
		self.assertNotRegex("wer", c.regular_expr["const_comp"])
		self.assertNotRegex("integral", c.regular_expr["const_comp"])
		self.assertNotRegex("derivative", c.regular_expr["const_comp"])
		self.assertNotRegex("solve", c.regular_expr["const_comp"])
		self.assertNotRegex("eval", c.regular_expr["const_comp"])

	def test_graph_comp(self):
		self.assertEqual(
			c.regular_expr["graph_comp"].search("graph x").group(1),
			"x")
		self.assertEqual(
			c.regular_expr["graph_comp"].search(
				"graph x and x^2").group(1),
			"x and x^2")
		self.assertEqual(
			c.regular_expr["graph_comp"].search(
				"graph x from 0 to 1").group(1),
			"x from 0 to 1")
		self.assertEqual(
			c.regular_expr["graph_comp"].search(
				"Graph 2*x").group(1),
			"2*x")

	def test_alg_comp(self):
		self.assertEqual(
			c.regular_expr["alg_comp"].search(
				"solve(x=2)").group(1),
			"(x=2)")
		self.assertEqual(
			c.regular_expr["alg_comp"].search(
				"Solve (x=3)").group(1),
			" (x=3)")

	def test_nested_alg_comp(self):
		self.assertEqual(
			c.regular_expr["alg_comp"].search(
				"solve(x=solve(x=4))").group(1),
			"(x=solve(x=4))")

	def test_eval_comp(self):
		m = c.regular_expr["eval_comp"].search("eval x at 1")
		self.assertEqual(m.group(1), "x")
		self.assertEqual(m.group(2), "1")

		m = c.regular_expr["eval_comp"].search("Eval 2*x at 3")
		self.assertEqual(m.group(1), "2*x")
		self.assertEqual(m.group(2), "3")

		m = c.regular_expr["eval_comp"].search("eval x^3 for .5")
		self.assertEqual(m.group(1), "x^3")
		self.assertEqual(m.group(2), ".5")

		m = c.regular_expr["eval_comp"].search("Eval 3*x for 11")
		self.assertEqual(m.group(1), "3*x")
		self.assertEqual(m.group(2), "11")

	@unittest.expectedFailure
	def test_nested_eval_comp(self):
		m = c.regular_expr["eval_comp"].search(
			"eval x at eval 2*x for 3")
		self.assertEqual(m.group(1), "x")
		self.assertEqual(m.group(2), "eval 2*x for 3")

	def test_der_comp(self):
		m = c.regular_expr["der_comp"].search(
			"derivative of x^2 at 2")
		self.assertEqual(m.group(1), "x^2")
		self.assertEqual(m.group(2), "2")
		
		m = c.regular_expr["der_comp"].search(
			"derivative of 3*x at 4")
		self.assertEqual(m.group(1), "3*x")
		self.assertEqual(m.group(2), "4")

		m = c.regular_expr["der_comp"].search(
			"derivative of 6*g at 1 with respect to g")
		self.assertEqual(m.group(1), "6*g")
		self.assertEqual(m.group(2), "1")
		self.assertEqual(m.group(3), " with respect to g")

	@unittest.expectedFailure
	def test_nested_der_comp(self):
		m = c.regular_expr["der_comp"].search(
			"derivative of 6*g at derivative of x^2 at 6 with "
			"respect to x with respect to g")
		self.assertEqual(m.group(1), "6*g")
		self.assertEqual(
			m.group(2),
			"derivative of x^2 at 6 with respect to x")
		self.assertEqual(m.group(3), " with respect to g")

	def test_int_comp(self):
		m = c.regular_expr["int_comp"].search(
			"integral 2*x dx 0 to 1")
		self.assertEqual(m.group(1), "2*x ")
		self.assertEqual(m.group(2), "x")
		self.assertEqual(m.group(3), "0")
		self.assertEqual(m.group(4), "1")
		
		m = c.regular_expr["int_comp"].search(
			"integral 2*x dx from 0 to 1")
		self.assertEqual(m.group(1), "2*x ")
		self.assertEqual(m.group(2), "x")
		self.assertEqual(m.group(3), "0")
		self.assertEqual(m.group(4), "1")
		
		m = c.regular_expr["int_comp"].search(
			"integrate 2*x dx 0 to 1")
		self.assertEqual(m.group(1), "2*x ")
		self.assertEqual(m.group(2), "x")
		self.assertEqual(m.group(3), "0")
		self.assertEqual(m.group(4), "1")

		m = c.regular_expr["int_comp"].search(
			"∫3*x dx 2 to 4")
		self.assertEqual(m.group(1), "3*x ")
		self.assertEqual(m.group(2), "x")
		self.assertEqual(m.group(3), "2")
		self.assertEqual(m.group(4), "4")

		m = c.regular_expr["int_comp"].search(
			"∫3*r dr 2 to 4")
		self.assertEqual(m.group(1), "3*r ")
		self.assertEqual(m.group(2), "r")
		self.assertEqual(m.group(3), "2")
		self.assertEqual(m.group(4), "4")

	@unittest.expectedFailure
	def test_int_comp_non_number_bounds(self):
		m = c.regular_expr["int_comp"].search(
			"integrate 2*x dx 0 to 1+1")
		self.assertEqual(m.group(1), "2*x ")
		self.assertEqual(m.group(2), "x")
		self.assertEqual(m.group(3), "0")
		self.assertEqual(m.group(4), "1+1")

	def test_comb_comp(self):
		self.assertRegex("C(5,4)", c.regular_expr["comb_comp"])
		self.assertRegex("P(5,4)", c.regular_expr["comb_comp"])

	def test_ave_comp(self):
		re = c.regular_expr["ave_comp"]

		self.assertRegex("Mean(4,3)", re)
		self.assertRegex("Median(4,3)", re)
		self.assertRegex("Mode(4,3)", re)
		self.assertRegex("mean(4,3)", re)
		self.assertRegex("median(4,3)", re)
		self.assertRegex("mode(4,3)", re)
		self.assertRegex("Max(4,3)", re)
		self.assertRegex("Min(4,3)", re)
		self.assertRegex("max(4,3)", re)
		self.assertRegex("min(4,3)", re)
		self.assertRegex("Ave(4,3)", re)
		self.assertRegex("ave(4,3)", re)
		self.assertRegex("average(4,3)", re)
		self.assertRegex("Stdev(4,3)", re)
		self.assertRegex("stdev(4,3)", re)

		m = c.regular_expr["ave_comp"].search("average(6,4)")
		self.assertEqual(m.group(1), "average")
		self.assertEqual(m.group(2), "(6,4)")

	def test_trig_comp(self):
		'''
		Test that all the single argument function get matched.
		'''

		for i in c.one_arg_funcs:
			with self.subTest(i = i):
				self.assertRegex(
					"%s(pi)" % i,
					c.regular_expr["trig_comp"])

	def test_gamma_comp(self):
		'''
		Test the gamma function regular expression.
		'''

		self.assertRegex("gamma(3)", c.regular_expr["gamma_comp"])
		self.assertRegex("Gamma(4)", c.regular_expr["gamma_comp"])
		self.assertRegex("Γ(3)", c.regular_expr["gamma_comp"])

	def test_log_comp(self):
		'''
		Test the logarithm regular expression.
		'''

		self.assertRegex("Log(4,2)", c.regular_expr["log_comp"])
		self.assertRegex("log(4,2)", c.regular_expr["log_comp"])
		self.assertRegex("Ln(2)", c.regular_expr["log_comp"])
		self.assertRegex("ln(4)", c.regular_expr["log_comp"])

	def test_mod2_comp(self):
		'''
		Test the mod function regular expression.
		'''

		self.assertRegex("mod(5,2)", c.regular_expr["mod2_comp"])
		self.assertRegex("Mod(5,2)", c.regular_expr["mod2_comp"])
		self.assertRegex("Mod(5,mod(8,6))", c.regular_expr["mod2_comp"])

	def test_abs_comp(self):
		'''
		Test the absolute value regular expression.
		'''

		self.assertRegex("|-1|", c.regular_expr["abs_comp"])
		self.assertRegex("|-1", c.regular_expr["abs_comp"])

	def test_paren_comp(self):
		'''
		Test the parentheses regular expression.
		'''

		self.assertRegex("(5+6)", c.regular_expr["paren_comp"])
		self.assertEqual(
			c.regular_expr["paren_comp"].search("(1+(2-1))").group(1),
			"2-1")

	def test_comma_comp(self):
		'''
		Test comma_comp.
		'''

		self.assertRegex("5,211", c.regular_expr["comma_comp"])
		self.assertNotRegex("5, 6", c.regular_expr["comma_comp"])

	def test_choose_comp(self):
		'''
		Test choose notation regular expression.
		'''

		self.assertRegex("5C3", c.regular_expr["choose_comp"])
		self.assertRegex("5P3", c.regular_expr["choose_comp"])
		self.assertRegex("5.4C3.1", c.regular_expr["choose_comp"])
		self.assertRegex("5.9P1.3", c.regular_expr["choose_comp"])

	def test_exp_comp(self):
		'''
		Test the exponents regular expression.
		'''

		self.assertRegex("2^3", c.regular_expr["exp_comp"])
		self.assertRegex("2**3", c.regular_expr["exp_comp"])
		self.assertRegex("2^3.1", c.regular_expr["exp_comp"])
		self.assertRegex("2**3.4", c.regular_expr["exp_comp"])
		self.assertRegex("2 ^ 3", c.regular_expr["exp_comp"])
		self.assertRegex("2 ** 3", c.regular_expr["exp_comp"])
		self.assertRegex("2 ^ 3.1", c.regular_expr["exp_comp"])
		self.assertRegex("2 ** 3.4", c.regular_expr["exp_comp"])

	def test_fact_comp(self):
		'''
		Test factorial regular expression.
		'''

		self.assertRegex("4!", c.regular_expr["fact_comp"])
		self.assertRegex(".7!", c.regular_expr["fact_comp"])
		self.assertRegex("4.2!", c.regular_expr["fact_comp"])
		self.assertRegex("-4.2!", c.regular_expr["fact_comp"])

	def test_mod_comp(self):
		'''
		Test the modulo operator regular expression.
		'''

		self.assertRegex("7 % 2", c.regular_expr["mod_comp"])
		
		m = c.regular_expr["mod_comp"].search("11%2")
		self.assertEqual(m.group(1), "11")
		self.assertEqual(m.group(2), "2")

	def test_per_comp(self):
		'''
		Test the percent regular expression.
		'''

		self.assertRegex("11%", c.regular_expr["per_comp"])

	def test_mult_comp(self):
		'''
		Test the multiplication and division regular expression.
		'''

		m = c.regular_expr["mult_comp"].search("11*2")
		self.assertEqual(m.group(1), "11")
		self.assertEqual(m.group(2), "*")
		self.assertEqual(m.group(3), "2")

		m = c.regular_expr["mult_comp"].search("11/2")
		self.assertEqual(m.group(1), "11")
		self.assertEqual(m.group(2), "/")
		self.assertEqual(m.group(3), "2")

		m = c.regular_expr["mult_comp"].search("10÷3")
		self.assertEqual(m.group(1), "10")
		self.assertEqual(m.group(2), "÷")
		self.assertEqual(m.group(3), "3")

	def test_add_comp(self):
		'''
		Test addition and subtraction regular expression.
		'''

		m = c.regular_expr["add_comp"].search("5-4")
		self.assertEqual(m.group(1), "5")
		self.assertEqual(m.group(2), "-")
		self.assertEqual(m.group(3), "4")

		m = c.regular_expr["add_comp"].search("1+3")
		self.assertEqual(m.group(1), "1")
		self.assertEqual(m.group(2), "+")
		self.assertEqual(m.group(3), "3")


class TestNonRepeatingLists(unittest.TestCase):
	'''
	Test that the NonRepeatingList class works as expected.
	'''

	def test_instantiate(self):
		nonlist = c.NonRepeatingList(1, 1, 2, 1)
		self.assertIsInstance(nonlist, c.NonRepeatingList)

	def test_str(self):
		nonlist = c.NonRepeatingList(1, 1, 2, 1)
		self.assertEqual(str(nonlist), "[1, 2, 1]")

	def test_indexing(self):
		nonlist = c.NonRepeatingList(1, 1, 2, 1)
		self.assertEqual(nonlist[0], 1)
		self.assertEqual(nonlist[-2], 2)
		self.assertEqual(nonlist[:2], [1, 2])

	def test_in(self):
		nonlist = c.NonRepeatingList(1, 1, 2, 1)
		self.assertIn(2, nonlist)

	def test_len(self):
		nonlist = c.NonRepeatingList(1, 1, 2, 1)
		self.assertEqual(len(nonlist), 3)

	def test_del(self):
		nonlist = c.NonRepeatingList(1, 1, 2, 1)
		del nonlist[1]
		self.assertEqual(len(nonlist), 1)

	def test_append(self):
		nonlist = c.NonRepeatingList(1)
		nonlist.append(4, 5, 5, 6)
		self.assertEqual(len(nonlist), 4)

	def test_clear(self):
		nonlist = c.NonRepeatingList(1, 1, 2, 1)
		nonlist.clear()
		self.assertEqual(nonlist, c.NonRepeatingList())

	def test_repr(self):
		nonlist = c.NonRepeatingList(1, 1, 2, 1)
		self.assertEqual(eval("c." + repr(nonlist)), nonlist)


class SimplifyMonoFunction(unittest.TestCase):
	'''
	Test the simplify function.
	'''

	def setUp(self):
		self.original_degree_mode = c.degree_mode
		c.switch_degree_mode(0)

	def tearDown(self):
		c.switch_degree_mode(self.original_degree_mode)

	def test_adding(self):
		self.assertEqual(c.simplify("1+1"), "2")
		self.assertEqual(c.simplify("1+6"), "7")
		self.assertEqual(c.simplify("2.9+3"), "5.9")
		self.assertEqual(c.simplify("2.9+3.6 + 1 + 4.11"), "11.61")

	def test_subtracting(self):
		self.assertEqual(c.simplify("1-1"), "0")
		self.assertEqual(c.simplify("21-4"), "17")
		self.assertEqual(c.simplify("2-4"), "-2")
		self.assertEqual(c.simplify("2.5-3"), "-0.5")
		self.assertEqual(c.simplify("7-3-7"), "-3")

	def test_multipling(self):
		self.assertEqual(c.simplify("54.8 * 1 -1"), "53.8")
		self.assertEqual(c.simplify("54.8 * -2"), "-109.6")
		self.assertEqual(c.simplify("54.8 * -2"), "-109.6")
		self.assertEqual(c.simplify("2.5 * 2.5"), "6.25")
		self.assertEqual(c.simplify("2 - 2 * 4 * 9 + 5"), "-65")
		self.assertEqual(c.simplify("2(1+1)"), "4")
		self.assertEqual(c.simplify("6(5-2)"), "18")
		self.assertAlmostEqual(
			float(c.simplify("2pi")),
			math.tau)

	def test_dividing(self):
		self.assertEqual(c.simplify("1 / 1"), "1")
		self.assertEqual(c.simplify("1 / 4 + 2"), "2.25")
		self.assertEqual(c.simplify("27 ÷3"), "9")
		self.assertEqual(c.simplify("1 + 27 /-6"), "-3.5")
		self.assertEqual(c.simplify("27 ÷-6 / .25"), "-18")

	def test_percentages(self):
		self.assertEqual(c.simplify("15%"), "0.15")
		self.assertEqual(c.simplify("136%"), "1.36")
		self.assertEqual(c.simplify(".6%"), "0.006")
		self.assertEqual(c.simplify("4*5%"), "0.2")

	def test_modulo(self):
		self.assertEqual(c.simplify("8%7 + 1"), "2")
		self.assertEqual(c.simplify("9%7"), "2")
		self.assertEqual(c.simplify("9%4"), "1")
		self.assertEqual(c.simplify("11%3 - 4"), "-2")
		self.assertAlmostEqual(
			float(c.simplify("8.9%1")),
			0.9)
		self.assertAlmostEqual(
			float(c.simplify("3*8.2%5%2")),
			3.6)

	def test_factorial(self):
		self.assertEqual(c.simplify("5!"), "120")
		self.assertEqual(c.simplify("3!"), "6")
		self.assertEqual(c.simplify("3!!"), "720")
		self.assertAlmostEqual(
			float(c.simplify("4.5!")),
			52.3427777846)

	def test_exponents(self):
		self.assertEqual(c.simplify("5^2"), "25")
		self.assertEqual(c.simplify("3^3"), "27")
		self.assertEqual(c.simplify("9^1.5"), "27")
		self.assertEqual(c.simplify("4^.5"), "2")
		self.assertEqual(c.simplify("4**2.5"), "32")
		self.assertEqual(c.simplify("1**41"), "1")

	def test_choose_notation(self):
		self.assertEqual(c.simplify("5C2"), "10")
		self.assertEqual(c.simplify("5C3"), "10")
		self.assertEqual(c.simplify("5P2"), "20")
		self.assertEqual(c.simplify("(2+3)C2"), "10")
		self.assertAlmostEqual(
			float(c.simplify("4.3 P 1.2")),
			5.589326932606859)

	def test_comma_comp(self):
		'''
		Test that commas still work when called from inside simplify.
		'''

		self.assertEqual(c.simplify("1,433,123"), "1433123")
		self.assertEqual(c.simplify("1,433,123.6"), "1433123.6")

	def test_comma_raises_error(self):
		with self.assertRaises(c.CalculatorError):
			c.simplify("2,3445.6")

	def test_parrentheses(self):
		self.assertEqual(c.simplify("(1-(3+4(3-2)-2))*-4+2"), "18")
		self.assertEqual(c.simplify("(((5*3)))"), "15")

	def test_absolute_value(self):
		self.assertEqual(c.simplify("|3-5|"), "2")
		self.assertEqual(c.simplify("|1-|3-5||"), "1")
		self.assertEqual(c.simplify("-|3-5|"), "-2")
		self.assertEqual(c.simplify("||6||"), "6")
		self.assertEqual(c.simplify("|-2*|6-|4+3|*2|+2|"), "14")

	def test_mod2(self):
		self.assertEqual(c.simplify("Mod(5,3)"), "2")
		self.assertEqual(c.simplify("mod(8,6)"), "2")
		self.assertEqual(c.simplify("mod(9,4)"), "1")
		self.assertEqual(c.simplify("mod(16,2)"), "0")
		self.assertAlmostEqual(float(c.simplify("mod(11.3,1)")), 0.3)
		self.assertEqual(c.simplify("mod(9*4,4)"), "0")
		self.assertEqual(c.simplify("mod(Mod(11,8),2)"), "1")
		self.assertEqual(c.simplify("mod(16.5,12**0)"), "0.5")

	def test_logarithm(self):
		self.assertEqual(c.simplify("Log(9,3)-1"), "1")
		self.assertEqual(c.simplify("log(27,9)"), "1.5")
		self.assertEqual(c.simplify("Log(1000,10)"), "3")
		self.assertEqual(c.simplify("Log(64,2)"), "6")
		self.assertEqual(c.simplify("Log(e^3,e)"), "3")
		self.assertEqual(c.simplify("ln(e)"), "1")
		self.assertEqual(c.simplify("Ln(e)"), "1")

	def test_gamma(self):
		self.assertEqual(c.simplify("gamma(6)"), "120")
		self.assertEqual(c.simplify("Γ(6)"), "120")
		self.assertEqual(c.simplify("Gamma(5)*.5"), "12")
		self.assertEqual(c.simplify("2^(Gamma(5)/8)"), "8")

	def test_single_argument_functions(self):
		self.assertAlmostEqual(
			float(c.simplify("sin(pi/2)")),
			1)
		self.assertAlmostEqual(
			float(c.simplify("cos(sin(pi))-2")),
			-1)
		self.assertAlmostEqual(
			float(c.simplify("4**floor(cos(6))")),
			1)








if __name__ == '__main__':
	for i in range(5):
		print("")
	doctest.testmod(c)
	unittest.main()
