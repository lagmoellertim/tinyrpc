import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setuptools.setup(
    name='tinyrpc',
    version='1.0.0',
    install_requires=requirements,
    license='MIT License',
    author='Tim-Luca Lagmöller',
    author_email='hello@lagmoellertim.de',
    description='Tiny RPC Library using Redis',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/lagmoellertim/tinyrpc',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
