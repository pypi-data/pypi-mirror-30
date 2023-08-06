from setuptools import setup, Extension

kw = dict(name="zstd._bindings", libraries=["zstd"])
try:
    from Cython.Build import cythonize
except ImportError:
    ext_modules = [Extension(sources=["zstd/_bindings.c"], **kw)]
else:
    ext_modules = cythonize([Extension(sources=["zstd/_bindings.pyx"], **kw)])

classifiers = """\
License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)
Programming Language :: Cython
Programming Language :: Python :: 2
Programming Language :: Python :: 3
"""

setup(
    name = 'cython-zstd',
    version = '0.1',
    description = 'Zstd bindings for Python',
    author = 'Nexedi',
    author_email = 'jm@nexedi.com',
    url = 'https://lab.nexedi.com/nexedi/cython-zstd',
    license = 'GPL 2+',
    classifiers=classifiers.splitlines(),
    packages = ['zstd'],
    ext_modules = ext_modules,
    test_suite='test',
)
