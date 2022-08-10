import setuptools

with open( "README.md", "r" ) as fh:
    long_description = fh.read()

setuptools.setup(
    name="eco_helper", 
    version="0.0.1",
    author="Noah H. Kleinschmidt",
    author_email="noah.kleinschmidt@students.unibe.ch",
    description="A command-line toolbox for data pre-processing streamlined to work with the EcoTyper framework.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/NoahHenrikKleinschmidt/eco_helper",
    
    packages=setuptools.find_packages(),
    package_data={'': ['*.r', '*.R']},

    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
    entry_points={
        "console_scripts": [ 
            "eco_helper=eco_helper.cli:main",
        ]
    },
    python_requires='>=3.6',
)