from distutils.core import setup

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except:
    long_description = None


setup(
  name = 'omakase',
  packages = ['omakase'],
  version = '0.5.5',
  description = 'My personal functions.',
  long_description = long_description,
  author = 'Adrian Kuhn',
  author_email = 'akuhnplus@gmail.com',
  url = 'https://github.com/akuhn/py-omakase',
  install_requires = ['forbiddenfruit'],
)
