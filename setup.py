import setuptools
import version

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setuptools.setup(
    name="splitter",
    version=version.VERSION,
    packages=["splitter"],
    package_dir={"": "src"},
    package_data={"splitter": ["*"]},
    install_requires=requirements,
    author="AXA",
    include_package_data=True,
    python_requires=">=3.8",
)
