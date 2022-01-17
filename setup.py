# Set up modules for the package
import setuptools
import os
setuptools.setup(
    name="umpkg",
    fullname="Ultramarine Packaging Tool",
    version="0.1.3",
    author="Cappy Ishihara",
    install_requires=[
        'typer',
        'koji',
        'python-gitlab',
        'configparser',
        'gitlab',
    ],
    include_dirs=['umpkg_cli'],
    include_package_data=True,
    scripts=['./umpkg'],
    packages=['umpkg_cli'],
    package_dir={'umpkg_cli': 'umpkg_cli'},
    python_requires='>=3.10',

)
