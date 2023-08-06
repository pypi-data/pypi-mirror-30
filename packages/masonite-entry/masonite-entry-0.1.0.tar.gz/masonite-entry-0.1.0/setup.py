from setuptools import setup

setup(
    name="masonite-entry",
    version='0.1.0',
    packages=['entry'],
    install_requires=[
        'masonite>=1.5,<= 1.5.99',
    ],
    include_package_data=True,
)
