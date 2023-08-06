from setuptools import setup

requirements = [l.strip() for l in open('requirements.txt').readlines()]


setup(
    name="easymap",
    version="0.0.1.dev1",
    py_modules=["easymap"],
    install_requires=requirements,
    include_package_data=True,

    # metadata for upload to PyPI
    author="Michael Zietz",
    author_email="michael.zietz@gmail.com",
    description="A simple tool for mapping data by political boundaries",
    license="MIT License",
    keywords="easymap map svg",
    url="https://github.com/zietzm/easymap",
)
