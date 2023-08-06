from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='py_pwned',
      version='0.1',
      description='Python3 Have I been Pwned checker',
      long_description=readme(),
      url='https://bitbucket.org/tvdsluijs/py_pwned',
      author='Theo van der Sluijs',
      author_email='theo@vandersluijs.nl',
      license='CC BY-NC-SA 4.0',
      classifiers=[
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
        ],
      keywords='pwned hacked passwords email e-mail',
      packages=['py_pwned'],
      install_requires=[
          'cfscrape',
          'getpass',
          'validate_email',
          'hashlib',
      ],
      zip_safe=False)