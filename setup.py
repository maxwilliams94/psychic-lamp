from setuptools import find_packages, setup
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the long description from the README file
long_description = (here / "README.md").read_text(encoding="utf-8")


setup(
    name="alpha_parse",
    version="0.0.1",
    description="Parsing Alpha Progressions exported output",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Max Williams",
    author_email="alphaparse@maxwillia.ms",
    classifiers=["Development Status :: 3 - Alpha"]
)