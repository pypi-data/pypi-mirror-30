from setuptools import find_packages,setup
packages=(find_packages())
setup(
    name= 'ThreadDownloader2211',
    version='1.1.2',
    description="my first python distribution",
    packages= packages,
    install_requires=["BeautifulSoup4"]
)