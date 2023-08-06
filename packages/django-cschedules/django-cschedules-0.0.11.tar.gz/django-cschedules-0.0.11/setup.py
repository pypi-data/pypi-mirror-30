import os
from setuptools import setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-cschedules',
    version='0.0.11',
    packages=['c_schedules'],
    include_package_data=True,
    license='BSD License',
    description='Very simple calendar schedule',
    long_description=README,
    url='http://git.dpsoft.org/puvka/cshedules.git',
    author='puvka',
    author_email='lendo.fox@gmail.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires=[
        'Django>=1.10.8,<=1.11.1',
        'django-extra-views',
        'requests==2.18.4',
    ]
)
