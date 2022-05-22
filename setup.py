from setuptools import setup, find_packages


setup(
    name='autowatch',
    version='2.0',
    description='Automatic hour fill for TimeWatch',
    url='https://github.com/danielattiach/autowatch',
    author='Daniel Attiach',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'beautifulsoup4==4.11.1',
        'python-dotenv==0.10.5',
        'requests==2.27.1',
    ],
)
