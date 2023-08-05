
#  ls.sampleproject
#  -----------

import codecs
from setuptools import setup, find_packages


setup(name="ls.sampleproject",
      use_scm_version={
          'write_to':  "ls/sampleproject/_version.py",
      },
      description="Prints 6x6 Sator Squares",
      long_description=codecs.open("README.rst", encoding="utf-8").read(),
      keywords=["sator", "rotas"],
      classifiers=["Intended Audience :: Developers",
                   "License :: OSI Approved :: MIT License",
                   "Operating System :: OS Independent",
                   "Programming Language :: Python",
                   "Topic :: Software Development :: Libraries :: Python Modules"
                  ],
      platforms="any",
      author="Dave Moore",
      author_email="dave@linuxsoftware.nz",
      url="https://github.com/linuxsoftware/ls.sampleproject",
      project_urls={
          'Source': "https://github.com/linuxsoftware/ls.sampleproject/",
          'Tracker': "https://github.com/linuxsoftware/ls.sampleproject/issues",
      },
      license="MIT",
      packages=find_packages(where=".", exclude=["ls.sampleproject.tests"]),
      setup_requires=["setuptools_scm"],
      install_requires=["inflect"],
      tests_require=["coverage"],
      #include_package_data=True,
      #package_data={},
      data_files=[
          ('my_data', ['data/data_file']),
      ],
      test_suite="ls.sampleproject.tests",
      zip_safe=False,
     )
