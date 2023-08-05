from setuptools import setup, find_packages

setup(
    # Application name:
    name="pivideo",

    # Version number (initial):
    version="0.1.13",

    # Application author details:
    author="Lintest Systems LLC",
    author_email="contact@lintestsystems.com",

    # Include additional files into the package
    #include_package_data=True,

    # Details
    url="http://lintestsystems.com/",

    # License
    license="MIT",

    # keywords
    keywords="PiCapture Raspberry Pi Video",

    classifiers=[
    # How mature is this project? Common values are
    #   3 - Alpha
    #   4 - Beta
    #   5 - Production/Stable
    'Development Status :: 5 - Production/Stable',

    # Pick your license as you wish (should match "license" above)
     'License :: OSI Approved :: MIT License',

    # Specify the Python versions you support here. In particular, ensure
    # that you indicate whether you support Python 2, Python 3 or both.
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.2',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    ],

    description="Raspberry Pi PiVideo Utilities for PiCapture",
    long_description=open("README.txt").read(),
    
    # Specify dependencies
	install_requires=['future'],
	
    # Modules
    py_modules=['pivideo','pivideo_class'],

    entry_points={
       'console_scripts': [
           'pivideo = pivideo:main',
       ],
    }

)