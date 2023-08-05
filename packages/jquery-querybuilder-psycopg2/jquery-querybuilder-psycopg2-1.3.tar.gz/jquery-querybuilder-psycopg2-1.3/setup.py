from setuptools import find_packages, setup

setup(
    name="jquery-querybuilder-psycopg2",
    version="1.3",

    description="Parse a jQuery QueryBuilder style rule set into a psycopg2.sql.Composable",
    url="https://bitbucket.org/gclinch/jquery-querybuilder-psycopg2",
    license="Apache License, Version 2.0",

    author="Graham Clinch",
    author_email="g.clinch@lancaster.ac.uk",

    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: Apache Software License",
        "Topic :: Database"],

    install_requires=["psycopg2"],

    package_data={"jquery_querybuilder_psycopg2": ["py.typed"]},

    packages=find_packages("src"),
    package_dir={"": "src"},
)
