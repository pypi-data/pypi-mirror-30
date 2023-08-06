from setuptools import setup
setup(
name = 'campyStructs',
packages = ['campyStructs'], # this must be the same as the name above
version = '1.0.0',
description = 'A collection of simple data structures in python',
author = 'Cameron MacArthur',
author_email = 'cam.mac@gmx.com',
license='MIT',
url = 'https://github.com/Cammac7/campyStructs', # use the URL to the github repo
download_url = 'https://github.com/Cammac7/campyStructs/archive/0.1.tar.gz', # I'll explain this in a second
keywords = ['data_structures', 'interviews', 'practice'], # arbitrary keywords
classifiers=[
#How mature is this project? Common values are
#   3 - Alpha
#   4 - Beta
#   5 - Production/Stable
'Development Status :: 3 - Alpha',

# Indicate who your project is intended for
'Intended Audience :: Developers',
'Topic :: Software Development :: Build Tools',

# Pick your license as you wish (should match "license" above)
'License :: OSI Approved :: MIT License',

# Specify the Python versions you support here. In particular, ensure
# that you indicate whether you support Python 2, Python 3 or both.
'Programming Language :: Python :: 3',
'Programming Language :: Python :: 3.2',
'Programming Language :: Python :: 3.3',
'Programming Language :: Python :: 3.4',
'Programming Language :: Python :: 3.5',
'Programming Language :: Python :: 3.6'
],
python_requires='>=3'
)
