from setuptools import setup, find_packages

#make version 1.0.0
setup(name='thundra',
      version='0.0.10',
      description='Thundra Python agent',
      url='https://github.com/thundra-io/thundra-lambda-agent-python',
      author='Thundra',
      author_email='support@thundra.io',
      packages=find_packages(exclude=('tests', 'tests.*',)),
      python_requires='>=3',
      zip_safe=True,
      )