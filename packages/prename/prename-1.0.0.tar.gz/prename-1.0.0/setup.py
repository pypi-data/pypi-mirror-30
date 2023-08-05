from setuptools import setup

setup(
    name='prename',
    version='1.0.0',
    description='Simple CLI tool for enacting regex renames',
    author='Rob Moore',
    author_email='giftiger.wunsch@xantoria.com',
    url='https://github.com/giftig/prename',
    download_url='https://github.com/giftig/prename/archive/1.0.tar.gz',
    keywords=['rename', 'renamer', 'regex renamer', 'regex', 'cli'],
    classifiers=[],
    packages=['prename'],
    entry_points={
        'console_scripts': [
            'prename = prename.prename:entrypoint'
        ]
    }
)
