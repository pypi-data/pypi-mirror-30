from setuptools import setup
from textwrap import dedent


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
    install_requires=[
        'kwrappers-s3ops==' + get_version(),
        'kwrappers-util==' + get_version(),
    ],
    zip_safe=False,
    data_files=['version.txt'],
)
