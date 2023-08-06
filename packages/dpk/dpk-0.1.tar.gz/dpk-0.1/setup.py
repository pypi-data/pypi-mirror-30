from distutils.core import setup
from setuptools import find_packages

setup(
    name='dpk',
    python_requires='>=3',
    version='0.1',
    author='7scientists GmbH',
    author_email='dpk-python@7scientists.com',
    license='MIT',
    url='https://github.com/dpkit/dpk-python',
    packages=find_packages(),
    package_data={'': ['*.ini']},
    include_package_data=True,
    install_requires=[],
    zip_safe=False,
    entry_points={
        'console_scripts': []
    },
    description='A Python library for communicating with a DPK server.',
    long_description="""A Python library for communicating with a DPK server."""
)
