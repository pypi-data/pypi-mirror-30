
import setuptools

with open('requirements.txt') as fp:
  requirements = fp.readlines()

setuptools.setup(
  name = 'nr.markdown',
  version = '1.0.3',
  author = 'Niklas Rosenstein',
  author_email = 'rosensteinniklas@gmail.com',
  license = 'MIT',
  description = 'Enhances the Misaka/Hoedown markdown parser.',
  url = 'https://github.com/NiklasRosenstein/py-nr.markdown',
  packages = setuptools.find_packages(),
  install_requires = requirements
)
