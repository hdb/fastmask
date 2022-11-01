from setuptools import setup, find_packages

exec(open('fastmask/version.py').read())

setup(
    name='fastmask',
    version=__version__,
    license='MIT',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click',
        'requests',
        'python-dotenv',
        'rich',
    ],
    entry_points={
        'console_scripts': [
            'fastmask = fastmask.cli:cli',
        ],
    },
)