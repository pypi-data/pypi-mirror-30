from setuptools import setup, find_packages

setup(
    name='chapman2',
    # version='0.0.0',
    version_format='{tag}.dev{commitcount}',
    setup_requires=['setuptools-git-version'],
    description='Chapman2 Task Queue',
    long_description='Some restructured text maybe',
    classifiers=[
        "Programming Language :: Python",
    ],
    author='Rick Copeland',
    author_email='rick@ehtcares.com',
    url='',
    keywords='',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[],
    tests_require=[],
    entry_points="""
    [console_scripts]
    c2 = chapman2.commands:main

    [chapman2.commands]
    init = chapman2.commands.init:Initialize
    shell = chapman2.commands.shell:Shell
    serve = chapman2.commands.serve:Serve
    """)
