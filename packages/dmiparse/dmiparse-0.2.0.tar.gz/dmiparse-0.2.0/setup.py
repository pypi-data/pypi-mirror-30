import setuptools

setuptools.setup(
    name="dmiparse",
    version="0.2.0",
    url="https://github.com/xmonader/dmiparse",

    author="Ahmed Youssef",
    author_email="xmonader@gmail.com",

    description="Parse dmidecode into reasonable python",
    long_description=open('README.md').read(),

    packages=setuptools.find_packages(),

    install_requires=[],

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
