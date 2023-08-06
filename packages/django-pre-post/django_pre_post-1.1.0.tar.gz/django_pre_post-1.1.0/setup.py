
import os

try:
    from setuptools import setup
    from setuptools import find_packages
except:  # noqa: E722
    from distutils.core import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


def read_requirements(fname):
    f = open(os.path.join(os.path.dirname(__file__), fname))
    return filter(lambda f: f != '', map(lambda f: f.strip(), f.readlines()))


setup(
    zip_safe=False,
    name="django_pre_post",
    version="1.1.0",
    author="Silly Inventor",
    author_email="SillyInventor@gmail.com",
    description="This package provides a framework for surveys and questionnaires",
    keywords="test, pre-post, questionnaire, survey",
    packages=find_packages(),
    long_description=read('README.md'),
    install_requires=read_requirements('requirements.txt'),
    test_suite="dummy",
    include_package_data=True,
)
