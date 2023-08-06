from termplanner.__init__ import __version__
from setuptools import setup, find_packages

setup(name='termplanner',
      version= __version__,
      py_modules=['termplanner'],
      install_requires=[
          'Click',
          ],
      entry_points='''
          [console_scripts]
          planner=termplanner.main:cli
      ''', # This is actually referring to a cli() function...
      description='A simple command line application to plan your day.',
      url='http://github.com/ModoUnreal/Planner',
      author='Alex Hurtado',
      author_email='modounreal@gmail.com',
      license='MIT',
      packages=find_packages(),
      zip_safe=False,
      classifiers=(
          'Development Status :: 4 - Beta',
          'Intended Audience :: Developers',
          'Natural Language :: English',
          'License :: OSI Approved :: MIT License',

          'Programming Language :: Python',
          'Programming Language :: Python :: 3'
          ),
)
