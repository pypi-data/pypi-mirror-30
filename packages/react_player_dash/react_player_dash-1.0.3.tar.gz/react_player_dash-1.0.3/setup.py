from setuptools import setup

exec (open('react_player_dash/version.py').read())

setup(
    name='react_player_dash',
    version=__version__,
    author='freshwuzhere',
    packages=['react_player_dash'],
    include_package_data=True,
    license='MIT',
    description='componentise the react-player to work with Dash',
    install_requires=[]
)
