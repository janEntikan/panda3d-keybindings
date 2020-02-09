"""A setuptools based setup module for the panda3d.keybindings package.
"""

from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.

setup(
    name='panda3d-keybindings',
    version='0.0.4b',
    description='A more abstract interface for using input devices in Panda3D.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/TheCheapestPixels/panda3d-keybindings',
    author='TheCheapestPixels',
    author_email='TheCheapestPixels@gmail.com',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    keywords='panda3d keybinding keybindings keymapping',
    package_dir={'': 'keybindings'},
    #packages=find_packages(where='keybindings'),
    packages=[''],
    python_requires='>=3.5, <4.*',
    install_requires=['panda3d'],
    ### Retained for cefconsole upgrade
    # extras_require={
    #     'cefconsole': ['panda3d-cefconsole'],
    # },
    # package_data={  # Optional
    #     'sample': ['package_data.dat'],
    # },
)
