from setuptools import setup, find_packages

setup(
    name='ConnyUtils',
    version='0.3',
    packages=find_packages(exclude=['tests*']),
    license='MIT',
    description='Some usefull functions for machine learning',
    long_description=open('README.txt').read(),
    install_requires=['numpy', 'pandas'],
    author='CPflaume',
    author_email='constantin.pflaume@gmail.com'
)
