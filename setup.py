import pathlib

from setuptools import setup, find_packages


README = (pathlib.Path(__file__).parent / 'README.md').read_text()

setup(
    name='auto-timewatch',
    version='2.0',
    description='Automatic hour fill for TimeWatch',
    url='https://github.com/danielattiach/autowatch',
    long_description=README,
    long_description_content_type='text/markdown',
    author='Daniel Attiach',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'beautifulsoup4==4.11.1',
        'python-dotenv==0.10.5',
        'requests==2.27.1',
    ],
)
