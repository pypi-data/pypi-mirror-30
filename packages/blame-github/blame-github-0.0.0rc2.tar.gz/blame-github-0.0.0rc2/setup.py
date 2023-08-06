from setuptools import setup
 
setup(
    name='blame-github',
    version='0.0.0rc2',
    description='',
    author='NyanKiyoshi',
    author_email='hello@vanille.bid',
    url='https://github.com/NyanKiyoshi/blame-github',
    py_modules=['blame_github'],
    entry_points="""
        [console_scripts]
        blame_github=blame_github:main
    """,
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3 :: Only',
    ],
    include_package_data=True,
    zip_safe=False,
    install_requires=[],
)
