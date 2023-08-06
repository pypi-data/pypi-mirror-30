from setuptools import setup, find_packages

setup(
    name="huepy",
    author="Somdev Sangwan",
    author_email="s0md3v@gmail.com",
    version="0.9.8.1",
    description="Print awesomely in terminals.",
    url="https://github.com/UltimateHackers/hue",
    download_url="https://github.com/UltimateHackers/hue/tarball/master",
    license='GNU General Public License v3 (GPLv3)',
    classifiers=[
        'Development Status :: 5 - Production/Stable',

        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    keywords='hue, huepy, terminal color, python color,',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),

)
