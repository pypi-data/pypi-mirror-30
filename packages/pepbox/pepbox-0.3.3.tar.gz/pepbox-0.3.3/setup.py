import os
import logging

from setuptools import setup

readme_dir = os.path.dirname(__file__)
readme_filename = os.path.join(readme_dir, 'README.md')

try:
    with open(readme_filename, 'r') as f:
        readme = f.read()
except:
    logging.warning("Failed to load %s" % readme_filename)
    readme = ""

try:
    import pypandoc
    readme = pypandoc.convert(readme, to='rst', format='md')
except:
    logging.warning("Conversion of long_description from MD to RST failed")
    pass

if __name__ == '__main__':
    setup(
        name='pepbox',
        version="0.3.3",
        description="Peptide specific TCR identification based on expansion.",
        author="Jerome Lane",
        author_email="jerome.lane@hotmail.com",
        url="",
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Environment :: Console',
            'Operating System :: OS Independent',
            'Intended Audience :: Science/Research',
            'Programming Language :: Python',
            'Topic :: Scientific/Engineering :: Bio-Informatics',
        ],
        install_requires=[
            'biopython',
            'numpy',
            'pandas',
            'python >= 2.7.13',
        ],
        long_description=readme,
        packages=['pepbox'],
    )