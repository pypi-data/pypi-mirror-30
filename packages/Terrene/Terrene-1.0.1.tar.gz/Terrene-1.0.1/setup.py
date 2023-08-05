from setuptools import setup, find_packages


required = [
    'beeprint', 'certifi', 'chardet', 'coreapi',
    'coreschema', 'h5py', 'idna', 'itypes',
    'Jinja2', 'MarkupSafe', 'numpy', 'pandas',
    'pkginfo', 'python-dateutil', 'pytz',
    'requests', 'requests-toolbelt', 'toolbelt',
    'six', 'tqdm', 'uritemplate', 'twine', 'urllib3',
    'urwid', 'uritemplate'
]

setup(
    name="Terrene",
    version="1.0.1",
    description="Terrene's Python SDK",
    url="https://docs.terrene.co",
    author="Terrene",
    author_email="developers@terrene.co",
    license='MIT',
    keywords="terrene",
    packages=find_packages(exclude=["test"]),
    install_requires=required,
    classifiers=[
        'Development Status :: 4 - Beta',

        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ]
)
