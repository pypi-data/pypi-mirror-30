from setuptools import setup

setup(
    name='yield-from',
    packages=['yieldfrom'],
    version='0.0.1',
    description='A backport of Python 3\'s "yield from" to Python 2.7.',
    license='MIT',
    author='H. Chase Stevens',
    author_email='chase@chasestevens.com',
    url='https://github.com/hchasestevens/yield-from',
    install_requires=[
        'asttools==0.1.1'
    ],
    entry_points={},
    keywords='backport compatibility generators',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
    ]
)
