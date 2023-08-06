import io
from setuptools import setup

# Version
version = open('VERSION.txt').read()

# Long description
try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
    long_description = long_description.replace("\r", "")
except (OSError, ImportError):
    print("Pandoc not found. Conversion of README.md to rst not available.")
    with io.open('README.md', encoding="utf-8") as f:
        long_description = f.read()

# Setup
setup(name='primo',
      version=version,
      description='Trading model framework',
      long_description=long_description,
      keywords=['quant', 'finance'],
      url='https://github.com/nhedlund/primo',
      author='nhedlund',
      license='MIT',
      packages=['primo'],
      zip_safe=False,
      install_requires=[
          'pandas >= 0.14',
          'numpy >= 1.8']
      )
