from distutils.core import setup
setup(
        name = 'hypnolog',
        packages = ['hypnolog'],
        version = '0.1.0',
        description = 'Python wrapper for quick logging using HypnoLog',
        author = 'SimonLdj',
        author_email = 'simon.ldj@gmail.com',
        url = 'https://github.com/SimonLdj/hypnolog-python',
        download_url = 'https://github.com/SimonLdj/hypnolog-python/archive/v0.1.0.tar.gz',
        keywords = ['hypnolog', 'debugging', 'debug', 'log', 'logging', 'console', 'visualization'],
        classifiers = [],
        install_requires=[
            'requests>=2.18.4',
            'jsonpickle>=0.9.6',
            ],
        license='MIT',
        )
