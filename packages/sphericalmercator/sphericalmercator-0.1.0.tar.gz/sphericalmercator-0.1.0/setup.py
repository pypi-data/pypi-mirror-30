from setuptools import setup

setup(
    name='sphericalmercator',
    version='0.1.0',
    py_modules = ['sphericalmercator',],
    description = 'Tool for calculate XYZ-tile bounding box in spherical mercator',
    long_description=open('README.rst').read(),
    url='https://bitbucket.org/lighter/spherical-mercator/',
    classifiers=[
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
    ],
    extras_require={
        'test': [
            'pytest',
        ],
    }
)
