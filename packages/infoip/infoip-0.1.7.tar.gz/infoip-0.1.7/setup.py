import os
import codecs

from setuptools import find_packages, setup

shortdesc = 'Get visitor geoip information from the request.'
longdesc = ''
for fname in ['README.rst', 'CONTRIBUTING.rst', 'CHANGES.rst', 'LICENSE.rst']:
    with codecs.open(fname, encoding='utf-8') as f:
        longdesc += f.read()
        longdesc += '\n'

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='infoip',
    version='0.1.7',
    packages=find_packages(),
    include_package_data=True,
    license='BSD',
    description=shortdesc,
    long_description=longdesc,
    url='https://github.com/ciokan/infoip-geoip-python-integrations',
    author='Romeo Mihalcea',
    author_email='romeo.mihalcea@gmail.com',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)