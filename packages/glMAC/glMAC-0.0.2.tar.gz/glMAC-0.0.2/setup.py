from distutils.core import setup

try:
    from pyqt_distutils.build_ui import build_ui
    cmdclass = {"build_ui": build_ui}
except ImportError:
    cmdclass = {}

setup(
    name='glMAC',
    version='0.0.2',
    author='gallochri',
    author_email='chri@gallochri.com',
    url='https://git.gallochri.com/gallochri/glMAC',
    download_url='https://git.gallochri.com/gallochri/glMAC.git',
    requires=['PyQt5', 'requests'],
    install_requires=['PyQt5', 'pyqt-distutils', 'requests'],
    provides=['glMAC'],
    keywords=['MAC', 'vendor', 'MAC Addresses'],
    description="Retrieves vendor information from MAC address",
    long_description="Utility to retrives vendor name from MAC address using api from macvendors.com",
    platforms='any',
    license='GPLv3',
    classifiers=['Development Status :: 2 - Pre-Alpha',
                 'Environment :: X11 Applications :: Qt',
                 'Intended Audience :: End Users/Desktop',
                 'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
                 'Natural Language :: English',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python :: 3.6',
                 'Topic :: System',
                 'Topic :: System :: Hardware'],
    packages=['glMAC', ],
    package_data={'glMAC': ['images/*', 'resources/*'], },
    entry_points={
        'console_scripts': [
            'glMAC=glMAC.__main__:main'
        ]
    },
    py_modules=['glMAC', ],
    cmdclass=cmdclass
    )
