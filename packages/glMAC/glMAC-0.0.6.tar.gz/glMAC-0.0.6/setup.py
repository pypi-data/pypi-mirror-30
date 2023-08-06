from setuptools import setup, find_packages
# from distutils.core import setup

try:
    from pyqt_distutils.build_ui import build_ui

    cmdclass = {"build_ui": build_ui}
except ImportError:
    cmdclass = {}

setup(
    name='glMAC',
    version='0.0.6',
    author='gallochri',
    author_email='chri@gallochri.com',
    url='https://git.gallochri.com/gallochri/glMAC',
    download_url='https://git.gallochri.com/gallochri/glMAC.git',
    python_requires='>=3.4',
    install_requires=[
        # PyQT5 dependency creates problems in packaging for opensuse
        # 'PyQt5',
        'requests'],
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
                 'Programming Language :: Python :: 3.4',
                 'Programming Language :: Python :: 3.5',
                 'Programming Language :: Python :: 3.6',
                 'Topic :: System',
                 'Topic :: System :: Hardware'],
    packages=find_packages(),
    package_data={'glMAC': ['images/*', 'resources/mainwindow.*']},
    entry_points={
        'console_scripts': [
            'glMAC=glMAC.__main__:main'
        ]
    },
    py_modules=['glMAC', ],
    cmdclass=cmdclass
)
