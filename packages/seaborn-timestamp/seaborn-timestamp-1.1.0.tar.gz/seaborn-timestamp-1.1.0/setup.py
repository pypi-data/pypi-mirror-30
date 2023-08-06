from setuptools import setup
import os

try:
    with open(os.path.join(os.path.dirname(__file__), 'README.md')) as f:
        long_description = f.read()
except IOError:
    long_description = ''

setup(
    name='seaborn-timestamp',
    version='1.1.0',
    description='Seaborn Timestamp has timing functions and a timing profile'
                ' which collects and reports on timing data of code execution',
    long_description=long_description,
    author='Ben Christenson',
    author_email='Python@BenChristenson.com',
    url='https://github.com/SeabornGames/Timestamp',
    install_requires=[
        'psycopg2',
    ],
    extras_require={
        'test':[
            'seaborn-file',
        ],
        'time-profile':[
            'seaborn-meta',
            'seaborn-table',
            'gevent',
        ],
    },
    packages=['seaborn_timestamp'],
    license='MIT License',
    classifiers=(
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: Other/Proprietary License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5'),
)
