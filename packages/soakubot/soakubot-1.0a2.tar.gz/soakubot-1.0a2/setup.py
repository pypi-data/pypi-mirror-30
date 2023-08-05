from setuptools import setup

setup(
    name='soakubot',
    packages=["soakubot"],
    version='1.0a2',
    install_requires=['requests>=2.18.4', 'colorama>=0.3.9', 'PyQuery>=1.4.0'],
    url='https://github.com/Soaku/OM-Bot',
    license="Just Don't Licence",
    author='Soaku',
    author_email='dominik@drozak.net',
    description="Bot API for OM games' forums."
)
