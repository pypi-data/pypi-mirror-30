from setuptools import setup

setup(
  name = 'pysp2tf_demo',
  version = '0.3',
  description = 'PySpark and TF demo',
  author = 'Andy Feng',
  author_email = 'andy.feng@gmail.com',
  url = 'https://github.com/anfeng/py-demo',
  keywords = ['tensorflow', 'spark'],
  packages = ['py2tf'],
  install_requires = ['pyspark'],
  license = 'Apache 2.0',
  classifiers = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: Apache Software License',
    'Topic :: Software Development :: Libraries',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6'
  ]
)