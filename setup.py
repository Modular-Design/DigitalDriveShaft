from setuptools import setup

# parse_requirements() returns generator of pip.req.InstallRequirement objects
with open("requirements.txt") as f:
    reqs = f.read().strip().split("\n")


setup(
    name="DigitalDriveShaft",
    classifiers=[
        "Programming Language :: Python :: 3.8",
    ],
    install_requires=reqs,
    extras_require={
        "develop": ["pytest>=7.1.1", "matplotlib>=3.5"],
        "ansys": " ansys-mapdl-core>=0.65.1",
    },
)
