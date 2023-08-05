from setuptools import setup

setup(
    name="masonite-entry",
    version='0.0.1',
    packages=['entry'],
    install_requires=[
        'masonite',
    ],
    include_package_data=True,
)
