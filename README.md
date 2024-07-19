# Python CLI EPUB Reader

Python CLI Epub reader with page navigation, bookmarks management, search management, save pages and book to text files and reading sessions to save and load your current progress

## Installation

You can install the package via pip:

```bash
pip install epub-reader
```

## Usage

After installation, you can run the EPUB reader from any directory:

```bash
epub-reader
```

This command will scan the current directory for EPUB files and allow you to read them interactively.

## Features

- Scans and lists EPUB files in any directory in which you run `epub-reader`
- Reads all HTML/XHTML pages in an EPUB file
- Extracts and displays title and author from EPUB metadata, and lists them as choices for the user to start reading the contents of the EPUB file
- Cleans and displays text content
- Allows navigation through pages with "n" (next), "p" (previous), "sp" (save page), "sb" (save book), "q" (quit), "j" (jump to page), "jp" (jump to percentage), "jb" (jump to bookmark), "db" (delete bookmark), "dab" (delete all bookmarks), "sh" (view search history), "ds" (delete search history), "das" (delete all search history), "al" (adjust lines per screen)
- Enhanced page lines depending on punctuation rather than HTML parsed content
- Save a page or the whole EPUB text to a text file `.txt`
- Saves reading session including current page, progress, bookmarks, and search history, and loading them so you never lose your progress.
- Colorized output for enhanced readability
- Graceful exit using `CTRL+C`

## Install Locally

to install locally, clone this repository and run:

```bash
git clone https://github.com/fairy-root/epub_reader.git
cd epub_reader
python setup.py install
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request if you have any ideas or find bugs.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.