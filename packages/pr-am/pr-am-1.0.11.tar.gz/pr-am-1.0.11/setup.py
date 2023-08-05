from setuptools import setup,find_packages

setup(
    name='pr-am',
    version='1.0.11',
    packages=['pr_am'],
    entry_points={
        'main_script': [
            'pr-am = pr_am.__main__:main'
        ]
    },
    description='Project Reality (BF2) Artillery Map',
    url='',
    author='Xembie',
    author_email='xembot@gmail.com',
    license="MIT",
    keywords="battlefield bf2 artillery map projectreality pr",
    install_requires=[
      'Pillow',
    ])
