import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-markdocs',
    version='1.0.0',
    packages=find_packages(),
    include_package_data=True,
    license='MIT License ',
    description='Generate static HTML pages from .md files.',
    long_description=README,
    url='https://github.com/aaronmarkey/django-markdocs',
    author='Aaron Markey',
    author_email='markeyaaron@gmail.com',
    install_requires=[
        'markdown',
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.0',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP',
    ],
)

