from distutils.core import setup
setup(
    name='geno',
    packages=['geno'],
    version='0.0.0.1',
    description='A solver for non-linear optimization problems.',
    author='Soeren Laue',
    author_email='soeren.laue@uni-jena.de',
    # I'll explain this in a second
    # download_url='https://github.com/peterldowns/mypackage/archive/0.1.tar.gz',
    package_data={'': ['license.txt'],
                  "pygeno": ["*.so"]},
    include_package_data=True,
    keywords=['solver', 'optimization'],
)
