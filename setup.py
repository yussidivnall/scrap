from setuptools import setup

with open("requirements.txt","r") as fp:
    requirements = fp.read().split()

setup(name='carscraper',
      version='0.1',
      description='Utilities for scraping pipelines',
      url='https://ctrlaltright.xyz',
      author='Jim',
      author_email='jim@ctrlaltright.xyz',
      license='',
      packages=['car_scraper', 'car_scraper.Har','car_scraper.Dom'],
      install_requires=requirements,
      zip_safe=False)
