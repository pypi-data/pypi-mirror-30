from setuptools import setup


def readme():
      with open('README.rst') as f:
            return f.read()

setup(name='readms-cli',
      version='0.1.1',
      description='A cli tool for downloading manga in https://readms.net',
      long_description=readme(),
      url='https://github.com/dslizardo/readms-cli',
      author='Daniel Lizardo',
      author_email='dslizardo@gmail.com',
      keywords='readms cli manga',
      license='MIT',
      packages=['readms'],
      install_requires=['setuptools','lxml','requests'],
      entry_points={
          'console_scripts': ['readms=readms.readms:main'],
      },
      include_package_data=True,
      zip_safe=False)