from setuptools import find_packages , setup

packages = find_packages()

setup(
    name="ThreadDownloader8010",
    version="1.1.0",
    description="My First Python Distribution",
    packages = packages,
    install_requires=["BeautifulSoup4"]

)

