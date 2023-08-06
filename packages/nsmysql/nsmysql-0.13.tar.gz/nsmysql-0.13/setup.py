from setuptools import setup

setup(name='nsmysql',
      version='0.13',
      description='Data exchange from net suite data to MySQL database, fixed encoding issue',
      url='https://github.com/ghao2/nsmysql',
      author='Guoxuan Hao',
      author_email='haoguoxuan@gmail.com',
      license='MIT',
      packages=['nsmysql'],
      install_requires=[
          'pymysql',
          'pandas',
          'numpy',
      ],
      zip_safe=False)