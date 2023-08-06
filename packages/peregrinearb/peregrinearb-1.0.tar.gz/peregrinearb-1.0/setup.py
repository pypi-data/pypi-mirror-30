from setuptools import setup


setup(
    name='peregrinearb',
    version='1.0',
    description='A Python library which provides several algorithms to detect arbitrage opportunities across over 90 cryptocurrency markets in 34 countries',
    author='Ward Bradt',
    author_email='wardbradt5@gmail.com',
    packages=['peregrine', 'peregrine.utils', 'peregrine.tests'],
    license='MIT',
    url='https://github.com/wardbradt/peregrine',

)
