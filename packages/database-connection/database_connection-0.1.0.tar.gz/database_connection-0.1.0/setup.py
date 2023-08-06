from setuptools import setup

setup(
      name='database_connection',
      version='0.1.0',
      description='A sqlalchemy connection utility',
      url='http://github.com/kkwanyang/database_connection',
      author='kkwanyang',
      author_email='kk.dsdev@gmail.com',
      license='MIT',
      packages=['database_connection'],
      zip_safe=False,

      install_requires=[
       'pymysql',
       'psycopg2',
       'sqlalchemy',
       'sqlalchemy-redshift'
      ],
      project_urls={
          'Source': 'https://github.com/kkwanyang/database_connection/',
          'Tracker': 'https://github.com/kkwanyang/database_connection/issues',
      }
)
