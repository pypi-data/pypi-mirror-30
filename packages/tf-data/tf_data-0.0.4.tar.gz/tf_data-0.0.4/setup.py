from setuptools import setup
setup(
    name='tf_data',
    packages=['tf_data'],
    version='0.0.4',
    description='Easy datasets for tensorflow',
    author='Florian Rueberg',
    author_email='florian.rueberg@gmail.com',
    url='https://github.com/fru/tf_data',
    download_url='https://github.com/fru/tf_data/archive/0.0.4.tar.gz',
    keywords=['datasets', 'tensorflow'],
    classifiers=[],
    install_requires=['requests', 'tqdm', 'tensorflow']
)
