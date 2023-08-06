from setuptools import setup

setup(
 name="biometal",
 version="0.1.0",
 description="Tools for dealing with metal binding sites.",
 url="https://biometal.samireland.com",
 author="Sam Ireland",
 author_email="mail@samireland.com",
 license="MIT",
 classifiers=[
  "Development Status :: 4 - Beta",
  "Intended Audience :: Science/Research",
  "License :: OSI Approved :: MIT License",
  "Topic :: Scientific/Engineering :: Chemistry",
  "Programming Language :: Python :: 3",
  "Programming Language :: Python :: 3.5",
  "Programming Language :: Python :: 3.6",
 ],
 keywords="chemistry bioinformatics proteins biochemistry metals",
 packages=["biometal"],
 install_requires=["atomium"]
)
