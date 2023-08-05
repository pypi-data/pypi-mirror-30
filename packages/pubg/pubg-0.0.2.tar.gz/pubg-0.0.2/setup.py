from setuptools import setup

setup(
    name='pubg',
    version='0.0.2',
    packages=['pubg'],
    url='https://github.com/nicolaskenner/python-pubg-api-wrapper',
    license='MIT',
    author='Nicolas Kenner',
    author_email='nick@nicolaskenner.com',
    description='Python wrapper for the Battlegrounds Developer API',
    install_requires=['requests'],
    classifiers=[
        'Development Status :: 1 - Planning',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6'
    ]
)
