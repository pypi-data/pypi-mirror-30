"""
Hans Roh 2015 -- http://osp.skitai.com
License: BSD
"""
import re
import sys
import os
import shutil, glob
import codecs
from warnings import warn
try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup

with open('tfserver/__init__.py', 'r') as fd:
	version = re.search(r'^__version__\s*=\s*"(.*?)"',fd.read(), re.M).group(1)

if sys.argv[-1] == 'publish':
	buildopt = ['sdist', 'upload']	
	if os.name == "nt":
		buildopt.insert (0, 'bdist_wheel')
	os.system('python setup.py %s' % " ".join (buildopt))
	for each in os.listdir ("dist"):
		os.remove (os.path.join ('dist', each))
	sys.exit()

elif sys.argv[-1] == 'develop':
	import site
	if os.name == "nt":
		linkdir = [each for each in site.getsitepackages() if each.endswith ("-packages")][0]		
	else:
		linkdir = [each for each in site.getsitepackages() if each.find ("/local/") !=- 1 and each.endswith ("-packages")][0]		
	target = os.path.join (os.path.join (os.getcwd (), os.path.dirname (__file__)), "tfserver")
	link = os.path.join (linkdir, "tfserver")
	if os.name == "nt":
		os.system ("mklink /d {} {}".format (link, target))
	else:
		os.system ("ln -s {} {}".format (target, link))	
	sys.exit ()
	
classifiers = [
  'License :: OSI Approved :: MIT License',
  'Development Status :: 4 - Beta',  
	'Intended Audience :: Developers',
	'Topic :: Scientific/Engineering :: Artificial Intelligence',
	'Programming Language :: Python',	
	'Programming Language :: Python :: 3'	
]

packages = [
	'tfserver',
	'tfserver.export',
	'tfserver.export.skitai',
]

package_dir = {'tfserver': 'tfserver'}
package_data = {}

install_requires = [
	'grpcio==1.4.0',
	'protobuf==3.4.0',
	'skitai'
]

with codecs.open ('README.rst', 'r', encoding='utf-8') as f:
	long_description = f.read()
    
setup(
	name='tfserver',
	version=version,
	description='Tensor Flow Model Server',
	long_description=long_description,
	url = 'https://gitlab.com/hansroh/tfserver',
	author='Hans Roh',
	author_email='hansroh@gmail.com',	
	packages=packages,
	package_dir=package_dir,
	package_data = package_data,
	license='MIT',
	platforms = ["posix"],
	download_url = "https://pypi.python.org/pypi/tfserver",
	install_requires = install_requires,
	classifiers=classifiers
)
