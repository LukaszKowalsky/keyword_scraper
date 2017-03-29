from setuptools import setup

setup(
    name='keyword_scraper',
    packages=['keyword_scraper'],
    version='1.0',
    include_package_data=True,
    install_requires=[
        'flask', 'requests', 'lxml'
    ],
)
