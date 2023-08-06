from setuptools import setup, find_packages
from os import path
import os
import sys

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

here = path.abspath(path.dirname(__file__))
long_description = """
Resize Command
===================
Discord Bots is a package that interacts with online Discord Bot Listing
websites, currently it supports updating the guild amount of a bot.
Installation:
-------------
pip:
~~~~
.. code:: bash
    $ pip install resize-cmd
    
Usage:
=========
.. code:: bash
    
"""
setup(name='Resize-CMD',
      version='1.0',
      packages=find_packages(),
      install_requires=['pillow'],
      author='JustMaffie',
      author_email='jori@justmaffie.nl',
      description='Resize images with a command',
      license='AGPL',
      long_description=long_description,
      url='https://justmaffie.nl',
      entry_points={'console_scripts':['resize=resize_cmd.commands:resize_command', 'size=resize_cmd.commands:size_command']}
      )