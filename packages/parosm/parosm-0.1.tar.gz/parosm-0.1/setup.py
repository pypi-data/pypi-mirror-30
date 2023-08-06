from setuptools import setup, find_packages


if __name__ == '__main__':
    with open('README.rst', 'r') as f:
        long_description = f.read()

    setup(
        name='parosm',
        version='0.1',
        description='OpenStreetMap Parser',
        long_description=long_description,
        url='https://github.com/DaGuich/parosm.git',
        keywords=[
            'parser',
            'osm',
            'openstreetmap'
        ],
        license='GPL Version 3',
        classifiers=[
            'Programming Language :: Python :: 3'
        ],
        packages=find_packages(exclude=['tests']),
        install_requires=[
            'protobuf',
            'defusedxml==0.5.0'
        ],
        entry_points={
            'console_scripts': [
                'osm2sql = parosm.prog.osm2sql.__init__:main',
                'osminfo = parosm.prog.osminfo.__init__:main'
            ]
        },
        test_suite='tests',
        python_requires='>=3.0.0',
    )
