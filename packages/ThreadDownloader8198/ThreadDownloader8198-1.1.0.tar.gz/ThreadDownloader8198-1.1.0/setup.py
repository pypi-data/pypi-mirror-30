from setuptools import find_packages, setup

packages = find_packages()

setup(
    name='ThreadDownloader8198',
    version='1.1.0',
    description="My first python distribution",
    packages=packages,
    install_requires=["BeautifulSoup4"]
)