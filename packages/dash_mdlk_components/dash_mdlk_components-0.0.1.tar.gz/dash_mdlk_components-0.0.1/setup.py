from setuptools import setup

exec (open('dash_mdlk_components/version.py').read())

setup(
    name='dash_mdlk_components',
    version=__version__,
    author='marcodlk',
    packages=['dash_mdlk_components'],
    include_package_data=True,
    license='MIT',
    description='Dash UI components developed by MDLK.',
    install_requires=[]
)
