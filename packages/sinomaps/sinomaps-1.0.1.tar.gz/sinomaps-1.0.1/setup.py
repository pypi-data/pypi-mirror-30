import os
import setuptools


setuptools.setup(
    name='sinomaps',
    version='1.0.1',
    keywords='teaching resource, high school',
    description='high school IT textbook resource, sinomaps version, 2018.',
    long_description=open(
        os.path.join(
            os.path.dirname(__file__),
            'README.rst'
        )
    ).read(),
    author='slobber',
    author_email='me@nandi.wang',
    url='https://www.sinomaps.com',
    packages=setuptools.find_packages(),
    install_requires=[
        'pandas>=0.22.0', 'matplotlib', 'numpy', 'itchat', 'requests>=2.18.0'
    ],
    license='BSD'
)