from setuptools import setup

version = '1.0.0'

setup(
    name = "atlas-cp",
    packages = ["atlas_cp"],
    python_requires='>=3',
    entry_points = {
        "console_scripts": ['atlas-cp = atlas_cp.atlas_cp:main']
        },
    version = version,
    description = 'Quickly add users to ATLAS CP server at Illinois',
    long_description = 'Quickly add users to ATLAS CP server at Illinois',
    author = 'Patrick Szuta',
    author_email = 'szuta@illinois.edu',
    url = 'https://git.math.illinois.edu/math-it/atlas-cp',
    project_urls = {
        'Source': 'https://git.math.illinois.edu/math-it/atlas-cp'
    },
    install_requires = [
        'requests',
        'urllib3',
        'ldap3'
    ]
)

