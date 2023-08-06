from distutils.core import setup

setup(
    name='py-auth0-jwt',
    version='0.2.8',
    packages=['pyauth0jwt',],
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    install_requires=["jwcrypto", "cryptography"],
)
