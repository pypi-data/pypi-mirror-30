from setuptools import setup

setup(
    name='badeeshello',
    version='0.1',
    license='BSD',
    author='Badees Nouiouat',
    author_email='badees98@gmail.com',
    url='http://www.experian.com',
    long_description="README.txt",
    packages=['badeeshello', 'badeeshello.images'],
    include_package_data=True,
    package_data={'badeeshello.images' : ['hello.gif']},
    description="Hello World testing setuptools",
)
