from setuptools import setup, find_packages
setup(
    name="bitsapi",
    version="0.1",
    packages=find_packages(),
    # scripts=['apirun.py'],

    # Project uses reStructuredText, so ensure that the docutils get
    # installed or upgraded on the target machine
    install_requires=['events', 'websocket-client', 'bit', 'pandas'],
    python_requires='>=3',

    package_data={
        # If any package contains *.txt or *.rst files, include them:
        '': ['*.csv', '*.rst'],
    },

    # metadata for upload to PyPI
    author="Expired Brain",
    author_email="invisible9007@gmail.com",
    description="This will help to get new tx notification from custom givenaddress.Theres no pain for address gap limit, balance forwarding, grab transactions info using 3rd party & writting all new incomming transaction to mysql.",
    license="PSF",
    keywords="pycoin, pywallet,",
    # url="",   # project home page, if any

    # could also include long_description, download_url, classifiers, etc.
)