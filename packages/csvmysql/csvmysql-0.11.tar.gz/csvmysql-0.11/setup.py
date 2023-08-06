from setuptools import setup

setup(name='csvmysql',
      version='0.11',
      description='transmit data from csv file to mysql database, date type is not handled in this version',
      url='https://github.com/ghao2/csvmysql',
      author='Guoxuan Hao',
      author_email='haoguoxuan@gmail.com',
      license='MIT',
      packages=['csvmysql'],
      install_requires=[
          'pymysql',
          'pandas',
          'numpy',
      ],
      zip_safe=False)