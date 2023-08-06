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

with open('skitai/__init__.py', 'r') as fd:
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
	target = os.path.join (os.path.join (os.getcwd (), os.path.dirname (__file__)), "skitai")
	link = os.path.join (linkdir, "skitai")
	if os.name == "nt":
		os.system ("mklink /d {} {}".format (link, target))
	else:
		os.system ("ln -s {} {}".format (target, link))	
	sys.exit ()
	
classifiers = [
  'License :: OSI Approved :: MIT License',
  'Development Status :: 4 - Beta',
  'Topic :: Internet :: WWW/HTTP :: HTTP Servers',	
	'Topic :: Internet :: WWW/HTTP :: WSGI',
	'Environment :: Console',
	'Environment :: No Input/Output (Daemon)',
	'Topic :: Internet',
	'Topic :: Software Development :: Libraries :: Python Modules',
	'Intended Audience :: Developers',
	'Programming Language :: Python',	
	'Programming Language :: Python :: 3',
	'Programming Language :: Python :: 3.4',
	'Programming Language :: Python :: 3.5',
]

packages = [
	'skitai',
	'skitai.bin',
	'skitai.server',
	'skitai.server.dbi',
	'skitai.server.wastuff',
	'skitai.server.handlers',
	'skitai.server.rpc',	
	'skitai.server.handlers.http2',
	'skitai.server.handlers.websocket',
	'skitai.server.handlers.proxy',
	'skitai.saddle',
	'skitai.saddle.patches',
	'skitai.saddle.contrib',
	'skitai.saddle.contrib.decorative',	
	'skitai.saddle.contrib.decorative.django',
]

package_dir = {'skitai': 'skitai'}
package_data = {
	"skitai": [
		"saddle/contrib/templates/*"
	]
}

install_requires = [
	"jinja2==2.9.4", 	
	"aquests",
	"sqlphile",
	"jsonrpclib-pelix"
]

with codecs.open ('README.rst', 'r', encoding='utf-8') as f:
	long_description = f.read()
    
setup(
	name='skitai',
	version=version,
	description='Skitai App Engine',
	long_description=long_description,
	url = 'https://gitlab.com/hansroh/skitai',
	author='Hans Roh',
	author_email='hansroh@gmail.com',	
	packages=packages,
	package_dir=package_dir,
	package_data = package_data,
	license='MIT',
	platforms = ["posix", "nt"],
	download_url = "https://pypi.python.org/pypi/skitai",
	install_requires = install_requires,
	classifiers=classifiers
)
