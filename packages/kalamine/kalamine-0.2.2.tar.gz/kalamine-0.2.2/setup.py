from setuptools import setup

with open('README.rst') as f:
    readme = f.read()

setup(
    name='kalamine',
    version='0.2.2',
    description='a yaml-centric Keyboard Layout Maker',
    long_description=readme,
    url='http://github.com/fabi1cazenave/kalamine',
    author='Fabien Cazenave',
    author_email='fabien@cazenave.cc',
    license='MIT',
    packages=['kalamine'],
    scripts=['bin/kalamine'],
    install_requires=['pyyaml'],
    include_package_data=True,
    zip_safe=False
)
