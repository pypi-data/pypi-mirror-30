from setuptools import setup, find_packages

setup(name="stapi",
      version="0.1.13",
      description="A Python client for accessing Star Trek API",
      long_description=open('README.rst').read(),
      url="https://github.com/mklucz/stapi-python",
      author="Maciej Kluczyński",
      author_email="maciej.lukasz.kluczynski@gmail.com",
      license="MIT",
      packages=find_packages(),
      zip_safe=False)

