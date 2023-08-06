"""
RecamanSequence
-------------

Simple script for iterating through Recaman's sequence up to a
given limit, where limit represent number of desired iterations.

You can get it by downloading it directly or by typing:

    $ pip install RecamanSequence

After it is installed you can start it by simply typing in your terminal:

    $ recaman 'integer_number_representing_desired_limit'

"""


from setuptools import setup

setup(name='RecamanSequence',
      version='0.1',
      description='Iterate through Recaman\'s sequence up to a given'
                  'limit, where limit represent number of desired iterations',
      long_description=__doc__,
      long_description_content_type='text/markdown',
      url="https://github.com/urosjevremovic/Recamans-Sequence",
      license='MIT',
      author='Uros Jevremovic',
      author_email='jevremovic.uros91@gmail.com',
      packages=['RecamanSequence'],
      entry_points={
          "console_scripts": ["recaman=RecamanSequence.recaman_sequence:main"],
      },
      )

__author__ = 'Uros Jevremovic'
