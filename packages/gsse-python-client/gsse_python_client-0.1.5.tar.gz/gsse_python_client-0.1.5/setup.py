from distutils.core import setup
setup(
    name = "gsse_python_client",
    packages = ["gsse_python_client"], # this must be the same as the name above
    version = "0.1.5",
    description = "Python client for global simualtion stock exchange",
    author = "Gabriel Berthling-Hansen",
    author_email = "gabrielbhansen@hotmail.com",
    url = "https://github.com/ogdans3/gsse-python-client", # use the URL to the github repo
    download_url = "https://github.com/ogdans3/gsse-python-client/archive/0.1.5.tar.gz",
    keywords = ["global", "simulated", "stock", "exchange"], # arbitrary keywords
    classifiers = [],

    # Dependent packages (distributions)
    install_requires=[
        "requests",
    ],
)