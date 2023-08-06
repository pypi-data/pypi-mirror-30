from setuptools import setup

version = '0.0.1'
classifiers = """\
License :: OSI Approved :: MIT License
Programming Language :: Python :: 3.7
"""

setup(
    name='kvae',
    version=version,
    description="keras varational_autoencoder as a package",
    keywords='vae variational autoencoder keras tensorflow',
    classifiers=[c for c in classifiers.split("\n") if c and c.strip()],
    author='Peter Waller',
    author_email='p@pwaller.net',
    url='http://github.com/pwaller/kvae/',
    license='MIT',
    py_modules=['kvae'],
    zip_safe=True,
)
