from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='interactive-components',
    version='1.0.0',
    author='Adrià Sarquella Farrés',
    license='MIT',
    author_email='adrisarquella@gmail.com',
    description='A set of tools to build useful components for interactive python scripts',
    #long_description=long_description, # TODO
    #long_description_content_type='text/markdown', # TODO
    #url='https://github.com/pypa/sampleproject',  # TODO
    # keywords='sample setuptools development',  # TODO
    packages=find_packages(),
    python_requires='>=3',
    classifiers=[
        'Development Status :: 5 - Production/Stable',

        'Environment :: Console',

        'Intended Audience :: Developers',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3 :: Only',

        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities'
    ],
    #project_urls={ # TODO
    #    'Bug Reports': 'https://github.com/pypa/sampleproject/issues',
    #    'Funding': 'https://donate.pypi.org',
    #    'Say Thanks!': 'http://saythanks.io/to/example',
    #    'Source': 'https://github.com/pypa/sampleproject/',
    #},
)