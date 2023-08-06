from setuptools import setup

setup(
    name='binaryrepr',
    version='0.15',
    author='David Lamouller',
    author_email='dlamouller@protonmail.com',
    py_modules=['binaryrepr'],
    install_requires=[
        'Click',
        'PrettyTable',
    ],
    description="binaryrep utility to display position of the bits for a number.",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Utilities'
    ],
    keywords='binary representation', 
    url='https://github.com/dlamouller/binaryreprtui',
    entry_points='''
        [console_scripts]
        binaryrepr=binaryrepr:binaryrepr
    ''',
)
