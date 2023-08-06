import os
from setuptools import setup
from textwrap import dedent


def get_all_install_requires():
    req_file_name = 'requirements.txt'
    req_files = [os.path.join(root, req_file_name) for root, dirs, files in os.walk('./') if req_file_name in files]
    return list({req for fl in req_files for req in get_install_requires(fl)})


def get_install_requires(file_path):
    with open(file_path, 'r') as f:
        return f.read().splitlines()


def get_version():
    with open('version.txt', 'r') as f:
        return f.readline().split()[0]  # Filter out other junk


# Completely unnessesary but testing bitbucket pipelines and observing PyPi files
def get_python_version(py_version):
    return "{}.{}".format(py_version.major, py_version.minor)


setup(
    name='kwrappers',
    version=get_version(),
    description='High level AWS operation library.',
    long_description=dedent("""The complete Kwrappers library for all manner of high level AWS operations. Some for
        perfomance, others encapsulation. Submodules are all available on their own."""),
    url='https://bitbucket.org/tim_kablamo/kwrappers',
    author='Tim Elson',
    author_email='tim.elson@kablamo.com.au',
    license='MIT',
    packages=['kwrappers_util/kwrappers/util', 'kwrappers_s3ops/kwrappers/s3ops'],
    install_requires=get_all_install_requires(),
    zip_safe=False,
    data_files=['version.txt'],
)
