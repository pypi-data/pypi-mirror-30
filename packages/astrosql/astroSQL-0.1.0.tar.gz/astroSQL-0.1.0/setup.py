from setuptools import setup, find_packages

setup(name='astroSQL',
      version='0.1.0',
      description='Simple API to access to existing astronomical MySQL database',
      url='https://github.com/ketozhang/astroSQL',
      author='Keto Zhang, Weikang Zheng',
      author_email='keto.zhang@gmail.com',
      packages=find_packages(),
      # data_files=[
      #       ('/path/to/write', ['path/to/data/file'])
      # ],
      install_requires=['peewee', 'termcolor', 'pymysql'],
      include_package_data=True,
      zip_safe=False)
