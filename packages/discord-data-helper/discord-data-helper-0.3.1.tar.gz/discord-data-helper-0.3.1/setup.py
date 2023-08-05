from setuptools import setup, find_packages

setup(name='discord-data-helper',
 
      version='0.3.1',
 
      url='https://github.com/DDH-MAKER/discord-data-helper',
 
      license='CCL',
 
      author='Helloyunho, func',
 
      author_email='rlacks628628@naver.com',
 
      description='Very simple to use module',
 
      packages=['ddh'],
 
      long_description=open('README.md').read(),
 
      zip_safe=False,
 
      setup_requires=['discord.py>=0.16.12'],
 
      test_suite='discord')