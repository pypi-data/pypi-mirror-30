from setuptools import setup, find_packages


def get_install_requires():
    with open('requirements.txt', 'r') as f:
        return f.read().splitlines()


def get_version():
    with open('version.txt', 'r') as f:
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
    packages=find_packages(),
    install_requires=get_install_requires().extend([
        "kwrappers-util==" + get_version(),
    ]),
    zip_safe=False,
    data_files=['version.txt'],
)
