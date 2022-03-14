from setuptools import setup
from pip.req import parse_requirements

# parse_requirements() returns generator of pip.req.InstallRequirement objects
install_reqs = parse_requirements(<requirements_path>)

# reqs is a list of requirement
# e.g. ['django==1.5.1', 'mezzanine==1.4.6']
reqs = [str(ir.req) for ir in install_reqs]


setup(
    name="DgitalDriveShaft",

    classifiers=[
        'Programming Language :: Python :: 3.8',
    ],
    install_requires=reqs,
    extras_require={
        'test': "pytest~=7.0.1",
    },

)