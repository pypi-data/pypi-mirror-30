# -.- coding: utf-8 -.-
from setuptools import setup, find_packages

try:
    from pyqt_distutils.build_ui import build_ui
    cmdclass = {"build_ui": build_ui}
except ImportError:
    cmdclass = {}

setup(
    name='glBooklet',
    version='0.0.1',
    author='gallchri',
    author_email='chri@gallochri.com',
    url='https://git.gallochri.com/gallochri/glBooklet',
    download_url='https://git.gallochri.com/gallochri/glBooklet.git',
    python_requires='>=3.4',
    install_requires=[
        # PyQT5 dependency creates problems in packaging for opensuse
        # 'PyQt5',
        'pyPdf2'],
    provides='glBooklet',
    keywords=['pdf', 'book', 'print'],
    description="Converts PDFs to printable booklet",
    long_description="Utility to convert a pdf book into 2 pages-per-sheet double sided booklet ready for printing",
    platforms='any',
    license='GPLv3',
    classifiers=['Development Status :: 2 - Pre-Alpha',
                 'Environment :: X11 Applications :: Qt',
                 'Intended Audience :: End Users/Desktop',
                 'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
                 'Natural Language :: English',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python :: 3.6',
                 'Topic :: Utilities',
                 'Topic :: Printing'],
    packages=find_packages(),
    package_data={'glBooklet': ['images/*', 'resources/*']},
    entry_points={
        'console_scripts': [
            'glBooklet=glBooklet.__main__:main'
        ]
    },
    py_modules=['glBooklet'],
    cmdclass=cmdclass
)
