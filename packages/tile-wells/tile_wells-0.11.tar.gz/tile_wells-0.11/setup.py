from setuptools import setup

setup(
    # Needed to silence warnings (and to be a worthwhile package)
    name='tile_wells',
    url='https://github.com/joelostblom/tile_wells/',
    author='Joel Ostblom',
    author_email='joel.ostblom@gmail.com',
    # Needed to actually package something
    packages=['tile_wells'],
    scripts=['bin/tile_wells'],
    # Needed for dependencies
    install_requires=['matplotlib', 'joblib'],
    # *strongly* suggested for sharing
    version='0.11',
    # The license can be anything you like
    license='MIT',
    description='''Place the well images of tiled fields in a layout similar to a multiwell
plate. This makes it easy to get an overview of the different conditions in
the plate.''',
    # We will also need a readme eventually (there will be a warning)
    # long_description=open('README.txt').read(),
)
