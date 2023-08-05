#   setup.py

import os
import pickle
from setuptools import setup, find_packages

setup(
    name = "ReCalc",
    version = "0.1.12",
    packages = find_packages(),
	# scripts = [
		# "ReCalc.py",
		# "testing_ReCalc.py",
		# "testing_ReCalc_tkinter.py"
	# ],
	
	classifiers = [
		"Programming Language :: Python :: 3.6",
		"Environment :: X11 Applications :: Gnome",
		"License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
		"Natural Language :: English",
		"Operating System :: Microsoft :: Windows :: Windows 10",
		"Operating System :: POSIX :: Linux",
		"Programming Language :: Python :: 3 :: Only",
		"Programming Language :: Python :: Implementation :: CPython",
		"Topic :: Scientific/Engineering :: Mathematics"
	],
	install_requires = [
		"sympy>=1.1.1",
		"pillow>=5.0.0",
		"docopt>=0.6.2",
		"numpy>=1.14.2",
	],
	
	package_data = {
	"": ["*.ico", "*.txt", "*.py"]
	},
	zip_safe = False,
	
	url = "https://github.com/RedKnite5/ReCalc.git",
	
	author = "Max Friedman",
	author_email = "mr.awesome10000@gmail.com",
	keywords = ["Calculator"]
)


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

calc_path = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(calc_path, "log_file.log"), "w+"):
	pass
with open(os.path.join(calc_path, "ReCalc_info.txt"), "wb+") as file:
	calc_info = {}
	calc_info["history"] = NonRepeatingList()
	calc_info["ans"] = 0
	calc_info["degree_mode"] = 0
	calc_info["polar_mode"] = False
	calc_info["der_approx"] = .0001
	calc_info["hist_len"] = 100
	calc_info["window_bounds"] = {
		"x min": -5,
		"x max": 5,
		"y min": -5,
		"y max": 5,
		"theta min": 0,
		"theta max": 10,
	}

	pickle.dump(calc_info, file)


