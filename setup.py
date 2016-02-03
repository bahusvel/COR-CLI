from setuptools import setup

setup(
    name='cor',
    version='0.1',
    py_modules=['cor', 'fscontroller', 'gitcontroller'],
    install_requires=[
        'Click',
        'PyGithub'
    ],
    entry_points='''
        [console_scripts]
        cor=cor:cor
    ''',
)