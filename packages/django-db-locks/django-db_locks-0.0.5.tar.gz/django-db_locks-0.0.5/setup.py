from setuptools import setup

setup(
    name='django-db_locks',
    version='0.0.5',
    packages=['locks', 'locks.management', 'locks.management.commands', 'locks.migrations'],
    url='https://github.com/BlockHub/django-locks',
    license='',
    author='Charles',
    author_email='karel@blockhub.nl',
    description='easy databaselocking for processes',
    install_requires=['django', 'psycopg2-binary']
)
