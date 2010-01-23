from distutils.core import setup



setup(
    name = "dregni",
    version = "0.1.dev1",
    author = "Marty Alchin",
    author_email = "gulopine@gamemusic.org",
    description = "A basic event management application for Django",
    # long_description = open("README").read(),
    license = "New BSD",
    url = "http://code.google.com/p/dregni/",
    packages = [
        "dregni",
        "dregni.templatetags",
    ],
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Framework :: Django",
    ]
)