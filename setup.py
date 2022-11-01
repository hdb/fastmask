from setuptools import setup, find_packages

setup(
    name='fastmask',
    version='0.1.0',
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