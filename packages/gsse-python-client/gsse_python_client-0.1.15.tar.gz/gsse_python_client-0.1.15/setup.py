from distutils.core import setup
version = "0.1.15"
setup(
    name = "gsse_python_client",
    packages = ["gsse_python_client"], # this must be the same as the name above
    version = version,
    description = "Python client for global simualtion stock exchange",
    author = "Gabriel Berthling-Hansen",
    author_email = "gabrielbhansen@hotmail.com",
    url = "https://github.com/ogdans3/gsse-python-client", # use the URL to the github repo
    download_url = "https://github.com/ogdans3/gsse-python-client/archive/" + version + ".tar.gz",
    keywords = ["global", "simulated", "stock", "exchange"], # arbitrary keywords
    classifiers = [],

    # Dependent packages (distributions)
    install_requires=[
        "requests",
        "requests_futures"
    ],
)