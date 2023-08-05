from setuptools import setup

exec (open('ace_components/version.py').read())

setup(
    name='ace_components',
    version=__version__,
    author='brymck',
    packages=['ace_components'],
    include_package_data=True,
    license='MIT',
    description='Ace editor component suite',
    install_requires=[]
)
