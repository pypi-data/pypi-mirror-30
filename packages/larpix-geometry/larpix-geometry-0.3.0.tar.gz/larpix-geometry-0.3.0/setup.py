'''
The setup.py file for larpix-geometry.

'''

from setuptools import setup, find_packages

setup(
        name='larpix-geometry',
        version='0.3.0',
        description='LArPix sensor plane geometry',
        url='https://github.com/samkohn/larpix-geometry',
        author='Sam Kohn',
        author_email='skohn@lbl.gov',
        keywords='dune physics',
        packages=find_packages(),
        install_requires=['pyyaml'],
        package_data={
            'larpixgeometry.layouts':['*.yaml']
        },
)
