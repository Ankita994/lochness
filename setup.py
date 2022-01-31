from distutils.core import setup
import setuptools
import os

with open("README.md", "r") as fh:
    long_description = fh.read()

here = os.path.abspath(os.path.dirname(__file__))

requirements= open('requirements.txt').read().split()

about = dict()
with open(os.path.join(here, 'lochness', '__version__.py'), 'r') as f:
    exec(f.read(), about)

setup(
    name=about['__title__'],
    version=about['__version__'],
    description=about['__description__'],
    author=about['__author__'],
    author_email=about['__author_email__'],
    url=about['__url__'],
    long_description=long_description,
    long_description_content_type="text/markdown",
    download_url='https://github.com/AMP-SCZ/lochness/archive/refs/tags/'
                 '{}.zip'.format(about['__version__']),
    keywords=['data', 'dataflow', 'download', 'datalake', 'U24'],
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires='>=3.7',
    install_requires=requirements,
    scripts=['scripts/listen_to_redcap.py',
             'scripts/lochness_create_template.py',
             'scripts/phoenix_generator.py',
             'scripts/lochness_check_config.py',
             'scripts/sync.py']
)
