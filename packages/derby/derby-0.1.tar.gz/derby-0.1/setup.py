from setuptools import setup

with open('README.md') as fd:
    description=fd.read()

setup(
    name='derby',
    version='0.1',
    packages=['derby',],
    keywords='dice rolling games',
    author="Micaiah Parker",
    author_email="me@micaiahparker.com",
    url='https://gitlab.com/micaiahparker/derby',
    license="MIT",
    description='A simple dice rolling library',
    long_description=description,
    classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3.6',
    ],
    project_urls = {
        'Source': 'https://gitlab.com/micaiahparker/derby'
    },
    install_requires=['lark-parser'],
    python_requires='>=3.6'
)