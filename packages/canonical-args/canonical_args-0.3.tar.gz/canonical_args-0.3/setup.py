from setuptools import setup, find_packages


description = "A module for dynamically registering, checking, and"\
			  " working with nested argument specs."
long_description = open("README.rst").read()

setup(name="canonical_args",
	  version="0.3",
	  description=description,
	  long_description=long_description,
	  author="Shonte Amato-Grill",
	  author_email="shonte.amatogrill@gmail.com",
	  maintainer="Shonte Amato-Grill",
	  maintainer_email="shonte.amatogrill@gmail.com",
	  url="https://github.com/shonteag/canonical_args",
	  packages=find_packages(exclude=["test", "tests"]),
	  classifiers=[
	      "Programming Language :: Python :: 2.7",
	      "Topic :: Software Development :: Libraries :: Python Modules",
	      "Intended Audience :: Developers"
	  ]
)
