from setuptools import setup, find_packages

setup (
  name='maximalexer',
  packages=find_packages(),
  version='1.0',
  author="F.M.Elwardi",
  author_email="elwardifadeli@gmail.com",
  description="A pygments lexer for Maxima (CAS) Code, based on asymptote lexer :)",
  license="MIT",
  keywords="maxima cas algebra lisp pygment plugins",
  classifiers=[
    # How mature is this project? Common values are
    #   3 - Alpha
    #   4 - Beta
    #   5 - Production/Stable
    'Development Status :: 4 - Beta',

    # Indicate who your project is intended for
    'Intended Audience :: Science/Research',
    'Topic :: Text Processing :: Filters',

    # Pick your license as you wish (should match "license" above)
     'License :: OSI Approved :: MIT License',

    # Specify the Python versions you support here. In particular, ensure
    # that you indicate whether you support Python 2, Python 3 or both.
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.2',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    ],
  url='https://github.com/foamscience/maximalexer/',
  entry_points =
  """
  [pygments.lexers]
  maximalexer = maximalexer.maximalexer:MaximaLexer
  """,
)
