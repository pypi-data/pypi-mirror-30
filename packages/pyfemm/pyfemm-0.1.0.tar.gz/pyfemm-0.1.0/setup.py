from setuptools import setup

setup(
    name='pyfemm',
    version='0.1.0',
    author='David Meeker',
    author_email='dmeeker@ieee.org',
    packages=['femm'],
    url='http://www.femm.info/wiki/pyFEMM',
    license=['LICENSE.txt'],
    description='Python interface to Finite Element Method Magnetics (FEMM)',
    long_description=open('README.txt').read(),
    install_requires=[
		'matplotlib',
		'pypiwin32',
		'six'
    ],
	classifiers=[
		"Development Status :: 3 - Alpha",
		"Intended Audience :: Science/Research",
		"Operating System :: Microsoft :: Windows",
		"Topic :: Scientific/Engineering :: Electronic Design Automation (EDA)",
		"License :: Aladdin Free Public License (AFPL)",
    ],
)
