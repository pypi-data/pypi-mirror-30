from setuptools import setup
import os

setup(name='ethnicity',
      version='0.0.1',
      description='Get ethnicity from name',
      long_description='',
      classifiers=[
      	'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3.6',
        "Topic :: Text Processing",
        "Topic :: Text Processing :: Filters"
      ],
      url='https://github.com/i9k/ethnicity',
      author='Igor Korostil',
      author_email='eeghor@gmail.com',
      license='MIT',
      packages=['ethnicity'],
      install_requires=['pandas'],
      python_requires='>=3.6',
      package_data={'ethnicity': ['data/*', 'race_/*']},
      keywords='ethnicity name')