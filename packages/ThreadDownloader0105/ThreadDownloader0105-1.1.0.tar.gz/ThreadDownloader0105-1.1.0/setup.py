from setuptools import find_packages,setup

# print(find_packages())
packages=find_packages()

setup(
    name='ThreadDownloader0105',
    # version='1.0.0',
    # version='1.0.1',
    version='1.1.0',
    description="My first python distribution",
    packages=packages,
    install_requires=["BeautifulSoup4"]
)