import multiprocessing
from setuptools import setup, find_packages
import iic4sem

setup(
    name='iic4sem',
    version=iic4sem.__version__,
    packages=find_packages(exclude=['*.pyc']),
    scripts=['bin/iic4sem'],
    url="https://github.com/xandfury/iic4sem",
    license='GPL 3',
    author="Abhinav Saxena",
    author_email="abhinav.saxena@iic.ac.in",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],
    project_urls={
        'Funding': 'http://iic.du.ac.in',
    },  
    keywords="IIC UDSC",
    include_package_data=True,
    long_description=open('README.md').read(),
    description="Basic Network Programming Assignments For IIC, UDSC 4 Sem Final",
    test_suite='nose.collector',
    tests_require="nose",
    install_requires=open('requirements.txt').read().splitlines()
)
