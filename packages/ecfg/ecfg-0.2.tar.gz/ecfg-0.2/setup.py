from setuptools import setup, find_packages


description = """
See `github repo <https://github.com/pior/ecfg>`_ for information.
"""


setup(
    name='ecfg',
    version='0.2',
    description='Python implementation for Shopify/ecfg',
    long_description=description,
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: Implementation :: PyPy",
        "License :: OSI Approved :: MIT License",
    ],
    keywords='secrets ejson crypto',
    author="Pior Bastida",
    author_email="pior@pbastida.net",
    url="https://github.com/pior/ecfg",
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=['PyNaCl'],
)
