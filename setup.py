import setuptools
import version

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setuptools.setup(
    name="axa-fr-splitter",
    version=version.VERSION,
    packages=["splitter"],
    package_dir={"": "src"},
    package_data={"splitter": ["*"]},
    install_requires=requirements,
    author="AXA",
    author_email="guillaume.chervet@axa.fr",
    url="https://github.com/AxaFrance/axa-fr-splitter",
    description="AXA France file splitter package",
    long_description="Utility library used to split pages from common file "
                     "types (pdf, tiff) into separate png files. It also "
                     "extracts text from input files.",
    classifiers=["Programming Language :: Python :: 3 :: Only",
                 "Programming Language :: Python :: 3.8",
                 "Topic :: Scientific/Engineering :: Information Analysis",
                 ],
    include_package_data=True,
    python_requires=">=3.8",
)
