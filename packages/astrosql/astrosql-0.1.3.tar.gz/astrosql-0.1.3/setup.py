from setuptools import setup, find_packages

setup(name='astrosql',
      version='0.1.3',
      description='Simple API to access to existing astronomical MySQL database',
      url='https://github.com/ketozhang/astroSQL',
      author='Keto Zhang, Weikang Zheng',
      author_email='keto.zhang@gmail.com',
      packages=['astrosql'],
      # data_files=[
      #       ('/path/to/write', ['path/to/data/file'])
      # ],
      install_requires=['peewee', 'termcolor', 'pymysql', 'astropy', 'numpy', 'pandas'],
      include_package_data=True,
      zip_safe=False)
