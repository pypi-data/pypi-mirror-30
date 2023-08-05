# -*- coding: utf-8 -*-

'''
Tkinter tests for ReCalc.

testing_ReCalc_tkinter.py
'''

import unittest
import tkinter as tk


class NonRepeatingList(object):
	'''
	A mutable list that doesn't have two of the same element in a row.
	
	>>> repr(NonRepeatingList(3, 3, 4))
	'NonRepeatingList(*[3, 4])'
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
		return("NonRepeatingList(*" + repr(self.items) + ")")

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


class HistorhLengthChanging(unittest.TestCase):
	
	def setUp(self):
		self.original_hist_len = c.hist_len		

	def test_change_hist_len(self):
		self.root = tk.Tk()
		self.entry = tk.Entry(self.root)
		self.root.update()
		self.entry.delete(0, "end")
		self.entry.insert(0, "20")
		self.root.update()
		c.change_hist_len(self.entry, self.root)
		self.assertEqual(c.hist_len, 20)
		self.assertEqual(c.calc_info["hist_len"], 20)
		
	def test_float_input(self):
		self.test_change_hist_len()
		self.root = tk.Tk()
		self.entry = tk.Entry(self.root)
		self.root.update()
		self.entry.delete(0, "end")
		self.entry.insert(0, 49.5)
		self.root.update()

		pre_hist_len = c.hist_len
		c.change_hist_len(self.entry, self.root)
		self.assertEqual(c.hist_len, pre_hist_len)
		self.assertEqual(c.calc_info["hist_len"], pre_hist_len)
		self.root.destroy()
		
	def test_other_string(self):
		self.test_change_hist_len()
		self.root = tk.Tk()
		self.entry = tk.Entry(self.root)
		self.root.update()
		self.entry.delete(0, "end")
		self.entry.insert(0, "hello")
		self.root.update()

		pre_hist_len = c.hist_len
		c.change_hist_len(self.entry, self.root)
		self.assertEqual(c.hist_len, pre_hist_len)
		self.assertEqual(c.calc_info["hist_len"], pre_hist_len)
		self.root.destroy()
		
	def test_string_int(self):
		self.root = tk.Tk()
		self.entry = tk.Entry(self.root)
		self.root.update()
		self.entry.delete(0, "end")
		self.entry.insert(0, "50")
		self.root.update()
		c.change_hist_len(self.entry, self.root)
		self.assertEqual(c.hist_len, 50)
		self.assertEqual(c.calc_info["hist_len"], 50)
		
	def tearDown(self):
		self.root = tk.Tk()
		self.entry = tk.Entry(self.root)
		self.root.update()
		self.entry.delete(0, "end")
		self.entry.insert(0, self.original_hist_len)
		self.root.update()
		c.change_hist_len(self.entry, self.root)

		
class ChangeDerApprox(unittest.TestCase):

	def setUp(self):
		self.original_der_approx = c.der_approx

	def test_change_der_approx_float(self):
		self.root = tk.Tk()
		self.entry = tk.Entry(self.root)
		self.root.update()
		self.entry.delete(0, "end")
		self.entry.insert(0, ".002")
		self.root.update()
		
		c.change_der_approx(self.entry, self.root)
		self.assertEqual(c.der_approx, .002)
		self.assertEqual(c.calc_info["der_approx"], .002)
		
	def test_der_approx_negative(self):
		self.root = tk.Tk()
		self.entry = tk.Entry(self.root)
		self.root.update()
		self.entry.delete(0, "end")
		self.entry.insert(0, "-.01")
		self.root.update()
		pre_der_approx = c.der_approx
		
		c.change_der_approx(self.entry, self.root)
		self.assertEqual(c.der_approx, pre_der_approx)
		self.assertEqual(c.calc_info["der_approx"], pre_der_approx)
		self.root.destroy()
		
	def test_der_approx_random_string(self):
		self.root = tk.Tk()
		self.entry = tk.Entry(self.root)
		self.root.update()
		self.entry.delete(0, "end")
		self.entry.insert(0, "word")
		self.root.update()
		pre_der_approx = c.der_approx

		c.change_der_approx(self.entry, self.root)
		self.assertEqual(c.der_approx, pre_der_approx)
		self.assertEqual(c.calc_info["der_approx"], pre_der_approx)
		self.root.destroy()


class ChangeGraphWinSet(unittest.TestCase):
	pass


class CartGraph(unittest.TestCase):
	
	def test_create_graph(self):
		g = c.CartGraph(
			xmin = -1, xmax = 1, ymin = 2, ymax = 3,
			wide = 40, high = 50)
		self.assertEqual(g.xmin, -1)
		self.assertEqual(g.xmax, 1)
		self.assertEqual(g.ymin, 2)
		self.assertEqual(g.ymax, 3)
		self.assertEqual(g.wide, 40)
		self.assertEqual(g.high, 50)
		g.root.destroy()
	
	def test_close_while_graphing(self):
		g = c.CartGraph(
			xmin = -1, xmax = 1, ymin = 2, ymax = 3,
			wide = 40, high = 50)
		g.draw("1")
		g.root.destroy()
		
	def test_graph_partial_undefined(self):
		g = c.CartGraph(
			xmin = -1, xmax = 1, ymin = 2, ymax = 3,
			wide = 100, high = 100)
		g.draw("x**.5")
		g.root.destroy()

		
class PolarGraph(unittest.TestCase):
	
	def test_create_graph(self):
		g = c.NumpyPolarGraph(
			xmin = -1, xmax = 1, ymin = 2, ymax = 3,
			theta_min = -2, theta_max = 6, wide = 40, high = 50)
		self.assertEqual(g.xmin, -1)
		self.assertEqual(g.xmax, 1)
		self.assertEqual(g.ymin, 2)
		self.assertEqual(g.ymax, 3)
		self.assertEqual(g.theta_min, -2)
		self.assertEqual(g.theta_max, 6)
		self.assertEqual(g.wide, 40)
		self.assertEqual(g.high, 50)
		g.root.destroy()
	
	def test_close_while_graphing(self):
		g = c.NumpyPolarGraph(
			xmin = -1, xmax = 1, ymin = 2, ymax = 3,
			theta_min = -.5, theta_max = .5, wide = 40, high = 50)
		g.draw("1")
		g.root.destroy()
		
	def test_graph_partial_undefined(self):
		g = c.NumpyPolarGraph(
			xmin = -1, xmax = 1, ymin = 2, ymax = 3,
			theta_min = -.5, theta_max = .5, wide = 100, high = 100)
		g.draw("x**.5")
		g.root.destroy()

		
class GraphFunction(unittest.TestCase):
	
	def setUp(self):
		self.mode = c.polar_mode
		c.switch_polar_mode(False)
		
	def test_basic_graph(self):
		g = c.graph_function("x")
		g.root.destroy()
		
	def test_graph_from(self):
		g = c.graph_function("x from 10 to 11")
		g.root.destroy()
		
	def test_multiple_graphs(self):
		g = c.graph_function("x and 2*x")
		g.root.destroy()
		
	def test_multiple_graphs_and_from(self):
		g = c.graph_function("x and 2*x from 10 to 11")
		g.root.destroy()

	def tearDown(self):
		c.switch_polar_mode(self.mode)


class GraphFunctionPolar(unittest.TestCase):
	
	def setUp(self):
		self.mode = c.polar_mode
		c.switch_polar_mode(True)
		
	def test_basic_graph(self):
		g = c.graph_function("x")
		g.root.destroy()
		
	def test_graph_from(self):
		g = c.graph_function("x from 10 to 11")
		g.root.destroy()
		
	def test_multiple_graphs(self):
		g = c.graph_function("x and 2*x")
		g.root.destroy()
		
	def test_multiple_graphs_and_from(self):
		g = c.graph_function("x and 2*x from 10 to 11")
		g.root.destroy()

	def tearDown(self):
		c.switch_polar_mode(self.mode)
































if __name__ == '__main__':
    unittest.main()
