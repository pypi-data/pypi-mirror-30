from setuptools import setup, find_packages
from operondemmo.version import version
self_version = version

try:
    LONG_DESCRIPTION = open("README.rst", "rb").read().decode("utf-8")
except IOError:
    LONG_DESCRIPTION = "an independent demo of KNOWN operon predict method"

setup(
    name='operondemmo',
    version=self_version,
    keywords='operon',
    packages=find_packages(),
    url='https://github.com/GodInLove/operondemmo',
    license='GPLv3',
    author='yaodongliu',
    author_email='yd.liu.scu@gmail.com',
    description="an independent demo of KNOWN operon predict method",
    long_description=LONG_DESCRIPTION,
    install_requires=[
        'numpy>=1.14',
        'pandas',
    ],
    entry_points={
        "console_scripts": ['operondemmo = operondemmo.operon:main']
    },
)
