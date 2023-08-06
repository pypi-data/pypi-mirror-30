# -*- coding: utf-8 -*-

import versioneer

from setuptools import setup, find_packages

with open('README.rst', 'r') as fp:
    readme = fp.read()


setup_args = {
    'name': 'nwb_docutils',
    'version': versioneer.get_version(),
    'cmdclass': versioneer.get_cmdclass(),
    'description': 'Collection of CLIs, scripts and modules useful to generate the NWB documentation',
    'long_description': readme,
    'long_description_content_type': 'text/x-rst; charset=UTF-8',
    'author': 'Oliver Ruebel',
    'author_email': 'oruebel@lbl.gov',
    'url': 'https://github.com/NeurodataWithoutBorders/nwb-docutils',
    'license': "BSD",
    'install_requires': [
        'matplotlib',
        'networkx',
        'pynwb',
        'pillow',
        'sphinx==1.6.5',
        'sphinx-gallery',
        'sphinx_rtd_theme'
    ],
    'setup_requires': 'pytest-runner',
    'packages': find_packages(),
    'package_data': {'nwb_docutils': ["*.ipynb"]},
    'entry_points': {
        'console_scripts': [
            'nwb_generate_format_docs=nwb_docutils.generate_format_docs:main',
            'nwb_init_sphinx_extension_doc=nwb_docutils.init_sphinx_extension_doc:main',
            'nwb_gallery_prototype=nwb_docutils.sg_prototype:main'
        ]
    },
    'classifiers': [
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: BSD License",
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",
        "Operating System :: Unix",
        "Topic :: Documentation :: Sphinx",
    ],
    'keywords': 'Neuroscience '
                'python '
                'HDF '
                'HDF5 '
                'cross-platform '
                'open-data '
                'data-format '
                'open-source '
                'open-science '
                'reproducible-research '
                'PyNWB '
                'NWB '
                'NWB:N '
                'NeurodataWithoutBorders',
    'zip_safe': False
}

if __name__ == '__main__':
    setup(**setup_args)
