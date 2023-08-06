import os
import sys

from awsassume import __version__
from setuptools import setup


sys.path.append(f'{os.getcwd()}/awsassume')
sys.path.append(f'{os.getcwd()}/tests')

readme = None
with open('README.rst', 'r') as file:
    readme = file.read()

setup(name='awsassume',
      version=__version__,
      description='Execute AWS CLI commands after assuming role',
      long_description=readme,
      url='https://github.com/zulhilmizainuddin/aws-assume',
      author='Zulhilmi Mohamed Zainuddin',
      author_email='zulhilmi.zainuddin@outlook.com',
      license='MIT',
      packages=['awsassume'],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3 :: Only',
          'Programming Language :: Python :: 3.6',
          'Environment :: Console'
      ],
      python_requires='>=3.6',
      install_requires=[
          'boto3>=1.6.16',
          'botocore>=1.9.16',
          'python-dateutil<2.7.0,>=2.1'
      ],
      tests_require=[
          'pytest>=3.5.0'
      ],
      setup_requires=[
          'pytest-runner>=4.2'
      ],
      entry_points={
          'console_scripts': [
              'awsassume=awsassume.__main__:console_entry'
          ]
      },
      test_suite='tests',
      zip_safe=False)
