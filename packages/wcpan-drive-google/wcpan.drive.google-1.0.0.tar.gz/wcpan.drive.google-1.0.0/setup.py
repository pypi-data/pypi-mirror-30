from setuptools import setup


setup(
        name='wcpan.drive.google',
        version='1.0.0',
        author='Wei-Cheng Pan',
        author_email='legnaleurc@gmail.com',
        description='Google Drive API with Tornado.',
        url='https://github.com/legnaleurc/wcpan.drive.google',
        packages=[
            'wcpan.drive.google',
        ],
        install_requires=[
            'PyYAML',
            'tornado',
            'wcpan.logger',
            'wcpan.worker >= 1.3',
        ],
        classifiers=[
            'Programming Language :: Python :: 3 :: Only',
            'Programming Language :: Python :: 3.5',
        ])
