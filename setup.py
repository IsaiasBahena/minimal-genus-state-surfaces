from setuptools import setup, find_packages

setup(
    name="minimal-genus-state-surfaces",
    version="0.1.0",
    description="Algorithms for computing minimal genus state surfaces from Gauss codes",
    author="Isaias Bahena, Thomas Kindred, Jason Parsley",
    package_dir={"":"src"},
    packages=find_packages(where="src"),
    python_requires=">=3.9",
)
