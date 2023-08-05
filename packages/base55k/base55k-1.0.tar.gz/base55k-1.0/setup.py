from setuptools import setup

setup \
(
    version="1.0",
    name="base55k",
    description="Convert decimal integers into a base 55296 system.",
    url="http://erbium.org",
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
    # scripts=["base55k.py"],
    zip_safe=False,
    python_requires=">=3",
)
