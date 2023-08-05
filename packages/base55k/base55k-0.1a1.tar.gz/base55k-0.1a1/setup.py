from distutils.core import setup

setup \
(
    version="0.1a1",
    name="base55k",
    description="A module for compressing integers into strings 1/4 of their original length, similar to hex system but with all characters that exist.",
    url="",
    author="Equation Kid",
    author_email="equationkid@gmail.com",
    packages=[],
    licence="MIT",
    keywords="base55k Base55k base Base 55 55k binary bin string str hex hexadecimal encode compress number integer int compressiontools compact",
    classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.2',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    ],
    zip_safe=False,
    python_requires=">=3",
)
