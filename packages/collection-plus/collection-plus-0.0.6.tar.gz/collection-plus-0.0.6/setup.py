from setuptools import setup, find_packages

setup(
    name='collection-plus',
    version='0.0.6',
    description='Collection utils',
    long_description=open('README.rst').read(),
    url='https://github.com/bruca/collections',
    author='Bruca Lock',
    author_email='lockshi@hotmail.com',
    keywords='collection collections',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    include_package_data=False,
    zip_safe=False
)