from setuptools import setup


setup(
    name="PyFireStore",
    version="0.1",
    author="Brice Parent - GingaLab",
    author_email="bparent@gingalab.com",
    description="Python wrapper around Google's FireStore API.",
    license="Apache",
    keywords="Python FireStore",
    url="https://bitbucket.org/gingalabdev/pyfirestore",
    packages=['pyfirestore'],
    long_description=open('README.md').read(),
    install_requires=['google-cloud-firestore>=0.28.0,<0.29'],
)
