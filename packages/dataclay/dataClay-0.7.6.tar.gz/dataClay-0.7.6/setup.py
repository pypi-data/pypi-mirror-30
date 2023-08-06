from setuptools import setup, find_packages

setup(name='dataClay',
      version='0.7.6',
      install_requires=["enum34",
                        "pyyaml",
                        "lru-dict",
                        "Jinja2",
                        "PyYAML",
                        "decorator",
                        "grpcio==1.10.1",
                        "grpcio-tools==1.10.1",
                        "protobuf",
                        "psutil"
                        ],
      description='Python library for dataClay',
      packages=find_packages("src"),
      package_dir={'':'src'},
      package_data={
        # All .properties files are valuable "package data"
        '': ['*.properties'],
      },
      )
