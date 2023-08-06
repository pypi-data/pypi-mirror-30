from setuptools import setup, find_packages

setup(name='cargo-api',
      version='0.3.0',
      description='API utility functions to handle API responses',
      url='https://gitlab.cargo.one/python/cargo-api',
      author='Mike Roetgers',
      author_email='mr@cargo.one',
      install_requires=[
          'pyjwt==1.6.1',
      ],
      license='MIT',
      packages=find_packages(),
      zip_safe=False)
