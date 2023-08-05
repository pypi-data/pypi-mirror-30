#   setup.py

from setuptools import setup, find_packages

setup(
    name = "ReCalc",
    version = "0.1.2",
    packages = find_packages(),
	scripts = [
		"ReCalc.py", "ReCalc_testing.py",
		"ReCalc_tkinter_testing.py"
	],
	
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
		"pillow>=5.0.0"
	],
	
	package_data = {
	"": ["*.ico", "*.txt", "*.py"]
	},
	zip_safe = False,
	
	url = "https://github.com/RedKnite5/ReCalc.git",
	
	author = "Max Friedman",
	author_email = "mr.awesome10000@gmail.com",
	desciption = "This is a basic graphing calculator.",
	licencse = "GPLv3",
	keywords = ["Calculator"]
)





