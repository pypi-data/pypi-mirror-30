from setuptools import setup

setup(
    name='redcap_report_generator',
    version='0.1.0',
    scripts=['redcap_report_generate.py'],
    install_requires=['PyCap','python-docx','argparse']
)
