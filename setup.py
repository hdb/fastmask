from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

exec(open('fastmask/version.py').read())

setup(
    name='fastmask',
    version=__version__,
    description='Python library + CLI for Fastmail masked email',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Hudson Bailey',
    author_email='dev@hudsonbailey.org',
    url='https://github.com/hdb/fastmask',
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click',
        'requests',
        'python-dotenv',
        'rich',
        'pandas',
    ],
    entry_points={
        'console_scripts': [
            'fastmask = fastmask.cli:cli',
        ],
    },
)