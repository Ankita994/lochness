from distutils.core import setup
import setuptools
import sys
from os.path import join

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='ampscz-lochness',
    version='v0.1.2',
    description='AMP-SCZ lochness',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='DPACC',
    author_email='kevincho@bwh.harvard.edu',
    url='https://github.com/AMP-SCZ/lochness',
    download_url='https://github.com/AMP-SCZ/lochness/archive/refs/tags/v0.1.0.zip',
    keywords=['data', 'dataflow', 'download', 'datalake', 'U24'],
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires='>=3.7',
    install_requires=['yaxil>=0.5.2',
                      'paramiko>=2.7.2',
                      'boxsdk>=2.11.0',
                      'jsonpath_ng>=1.5.2',
                      'cryptease>=0.2.0',
                      'pytz>=2021.1',
                      'requests>=2.26.0',
                      'six>=1.16.0',
                      'pandas>=1.3.2',
                      'pytest>=6.2.4',
                      'numpy>=1.20.3',
                      'mano>=0.5.1',
                      'LAMP>=0.0.1',
                      'PyYAML>=6.0'],
    scripts=['scripts/listen_to_redcap.py',
             'scripts/lochness_create_template.py',
             'scripts/phoenix_generator.py',
             'scripts/lochness_check_config.py',
             'scripts/sync.py']
)
