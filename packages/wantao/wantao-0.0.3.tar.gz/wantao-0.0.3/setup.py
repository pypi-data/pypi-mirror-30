from distutils.core import setup
from setuptools import setup, find_packages

setup(
    name = 'wantao',
    keyword='wantao',
    version ='0.0.3',
    description = 'just a simple test',
    license = 'MIT License',
    url='https://github.com/wantao666/wantao',
    author = 'wantao',
    author_email = '895484122@qq.com',
    include_package_data=True,
    packages = find_packages(),
    install_requires=['requests>=2.0','httplib2>=0.9'],
    zip_safe=False,
)