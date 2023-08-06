# from distutils.core import setup
import SamAuthenticator.Meta
import os
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

try:
    del os.link
except:
    pass

include_files = ["SamAuthenticator/images/key.png"]

setup(
    name="samauth",
    version = SamAuthenticator.Meta.__version__,
    author="Samer Afach",
    author_email="samer@afach.de",
    packages=["SamAuthenticator"],
    include_package_data=True,
    url="https://git.afach.de/samerafach/SamAuthenticator",
    description="A simple Google Authenticator replacement",
    data_files=include_files,
    install_requires=['pyqt5', 'onetimepass', 'cryptography', 'argon2'],
    extras_requires=['pyqt5', 'onetimepass', 'cryptography', 'argon2'],
    python_requires='>=3.4',
    entry_points={
        'console_scripts': [
            'samauth          = SamAuthenticator.AuthenticatorGUIApp:start',
            'samauthenticator = SamAuthenticator.AuthenticatorGUIApp:start'
        ]}
)
