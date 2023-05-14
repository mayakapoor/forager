import setuptools

with open("README.md", "r", encoding = "utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name = "forager-toolkit",
    version = "1.8",
    author = "Maya Kapoor",
    author_email = "mkapoor1@uncc.edu",
    description = "A network traffic classification toolkit",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "https://github.com/mayakapoor/forager",
    project_urls = {
        "Bug Tracker": "https://github.com/mayakapoor/forager/issues",
        "Documentation": "https://forager-toolkit.readthedocs.io/en/latest/"
    },
    classifiers = [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    py_modules=[
        "forager"
    ],
    entry_points={
        "console_scripts": [
            "forager = forager:main",
        ]
    },
    package_dir = {"": "src"},
    packages = setuptools.find_packages(where="src"),
    install_requires=[
          'tapcap',
          'rexactor'
      ],
    python_requires = ">=3.6"
)
