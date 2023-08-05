from setuptools import setup

setup(
    name='hyperswitch',
    version='0.1',
    description='A context switching application for Linux',
    url='https://bitbucket.org/TheNoctambulist/hyperswitch/',
    author='TheNoctambulist',
    author_email='TheNoctambulist@zoho.com',
    license='MIT License',
    zip_safe=False,
    packages=['hyperswitch'],
    package_data={
        '': ['*.txt', '*.rst']
    },
    entry_points={
        'gui_scripts': [
            'hyperswitch = hyperswitch:main'
        ]
    },
    install_requires=[
        "ewmh"
    ]
)
