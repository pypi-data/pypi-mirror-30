from setuptools import setup

setup(name='ggshmysql',
      version='0.13',
      description='Data exchange from Google Sheet to MySQL database, fixed encoding issue',
      url='https://github.com/ghao2/ggshmysql',
      author='Guoxuan Hao',
      author_email='haoguoxuan@gmail.com',
      license='MIT',
      packages=['ggshmysql'],
      install_requires=[
          'pymysql',
          'pandas',
          'numpy',
          'gsheets'
      ],
      zip_safe=False)