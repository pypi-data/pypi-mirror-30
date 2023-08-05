from setuptools import setup, find_packages

with open("qth_darksky/version.py", "r") as f:
    exec(f.read())

setup(
    name="qth_darksky",
    version=__version__,
    packages=find_packages(),

    # Metadata for PyPi
    url="https://github.com/mossblaser/qth_darksky",
    author="Jonathan Heathcote",
    description="Inject weather forecasts from Darksky.net into Qth",
    license="GPLv2",
    classifiers=[
        "Development Status :: 3 - Alpha",

        "Intended Audience :: Developers",

        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",

        "Operating System :: POSIX :: Linux",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",

        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
    ],
    keywords="qth home-automation weather",

    # Requirements
    install_requires=["qth>=0.6.0", "requests>=2.0.0"],

    # Scripts
    entry_points={
        "console_scripts": [
            "qth_darksky = qth_darksky:main",
        ],
    }
)
