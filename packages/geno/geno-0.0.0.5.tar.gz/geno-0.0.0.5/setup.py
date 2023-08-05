from distutils.core import setup
setup(
    name='geno',
    packages=['geno'],
    version='0.0.0.5',
    description='A solver for non-linear optimization problems.',
    author='Soeren Laue',
    author_email='soeren.laue@uni-jena.de',
    package_data={'': ['license.txt'],
                  "geno": ["*.so"],
                  "scripts": ["*.py"]},
    include_package_data=True,
    keywords=['solver', 'optimization'],
)
