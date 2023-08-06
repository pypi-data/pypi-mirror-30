# coding: utf-8

from setuptools import setup
from flake8_gramex import __version__ as version

setup(
    name='flake8-gramex',
    version=version,
    description="Additional validations for Python code",
    long_description='Test unicode errors, special numbers, etc',
    keywords=['flake8', 'encoding', 'unicode'],
    author='Suhas',
    author_email='suhas@gramener.com',
    url='https://gramener.com/',
    license='MIT',
    py_modules=['flake8_gramex'],
    zip_safe=False,
    entry_points={
        'flake8.extension': [
            'flake8_gramex = flake8_gramex:CheckErrors',
        ],
    },
    install_requires=[
        'flake8',
    ],
    tests_require=[
        'nose',
        'flake8'
    ],
    test_suite="nose.collector",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Quality Assurance',
    ],
)
