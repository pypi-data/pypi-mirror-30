from setuptools import setup
import os

here = os.path.dirname(os.path.realpath(__file__))


def get_install_requires():
    with open(os.path.join(here, 'requirements.txt'), 'r') as f:
        return f.read().splitlines()


def get_version():
    with open(os.path.join(here, '..', 'version.txt'), 'r') as f:
        return f.readline().split()[0]  # Filter out other junk


# Completely unnessesary but testing bitbucket pipelines and observing PyPi files
def get_python_version(py_version):
    return "{}.{}".format(py_version.major, py_version.minor)


setup(
    name='kwrappers_s3ops',
    version=get_version(),
    description='S3 operations.',
    long_description='AWS orchestration tools for dealing with S3.',
    url='https://bitbucket.org/tim_kablamo/kwrappers',
    author='Tim Elson',
    author_email='tim.elson@kablamo.com.au',
    license='MIT',
    packages=['kwrappers.s3ops'],
    install_requires=get_install_requires(),
    zip_safe=False,
)
