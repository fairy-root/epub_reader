from setuptools import setup, find_packages

setup(
    name='epub-reader',
    version='1.0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'beautifulsoup4',
    ],
    entry_points={
        'console_scripts': [
            'epub-reader=epub_reader.main:main',
        ],
    },
    author='fairy-root',
    author_email='fairyvmos@gmail.com',
    description='Python CLI Epub reader with page navigation, bookmarks management, search management, save pages and book to text files and reading sessions to save and load your current progress ',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/fairy-root/epub_reader',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)