import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="open_telemetry_kit",
    version="0.2.6.4",
    author="Hivemapper",
    author_email="adam@hivemapper.com",
    description="Open source package for extracting and parsing telemetry associated with video streams and converting to common formats.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Hivemapper/open-telemetry-kit",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "Intended Audience :: Developers",
        "Operating System :: POSIX :: Linux",
        "Topic :: Multimedia :: Video",
        "Topic :: Scientific/Engineering :: GIS",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "Topic :: Software Development :: Libraries",
        "Topic :: Text Processing"
    ],
    python_requires='>=3.6',
)
