from setuptools import setup, find_packages

setup(
    name='reweave',
    version='0.1.1',
    description='Reave is a AI automated video creator',
    author='Chandresh',
    author_email='chandresh.code@gmail.com',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'requests',
        'openai',
        'moviepy',
        'pydantic'
    ],
)
