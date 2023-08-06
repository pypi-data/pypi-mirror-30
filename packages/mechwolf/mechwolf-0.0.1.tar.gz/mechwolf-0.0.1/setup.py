from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
# with open(path.join(here, 'readme.md')) as f:
#     long_description = f.read()

setup(
    name='mechwolf',  # Required
    version='0.0.1',  # Required
    description='Placeholder deploy for MechWolf',  # Required
    long_description="Placeholder deploy for MechWolf",  # Optional
    url='https://github.com/benjamin-lee/MechWolf',  # Optional
    author='Benjamin Lee and Alex Mijalis',  # Optional
    author_email='benjamindlee@me.com',  # Optional
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        "Intended Audience :: Science/Research",
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Manufacturing",
        "Topic :: Scientific/Engineering :: Chemistry",
        'Programming Language :: Python :: 3.6',
    ],
    packages=find_packages(),  # Required
    # setup_requires=['cython'],
    tests_require=["pytest"],
    install_requires=[
        "graphviz",
        "terminaltables",
        "pint",
        "plotly",
        "networkx",
        "CIRpy",
        "colorama",
        "pyserial",
        "pyyaml",
        "flask",
        "aiohttp",
        "vedis",
        "schedule",
        "requests",
        "sphinx",
        "numpy",
        "pandas",
        "xkcdpass",
        "pick",
        "click",
        "rsa",
        "yamlordereddictloader"],

    # entry_points={  # Optional
    #     'console_scripts': [
    #         'sample=sample:main',
    #     ],
    # },
)
