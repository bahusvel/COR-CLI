from setuptools import setup

setup(
    name='cor',
    version='0.1',
    py_modules=['cor', 'fscontroller', 'gitcontroller'],
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        yourscript=yourscript:cli
    ''',
)