import os
import zipfile
import re
import json
from typing import List, Tuple, Dict
from bs4 import BeautifulSoup

GLOBAL_SETTINGS_FILE = os.path.join(os.path.expanduser("~"), ".epub_reader", "global_settings.json")

def load_global_settings() -> Dict:
    if os.path.exists(GLOBAL_SETTINGS_FILE):
        with open(GLOBAL_SETTINGS_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    return {"lines_per_screen": 40}

def save_global_settings(settings: Dict) -> None:
    os.makedirs(os.path.dirname(GLOBAL_SETTINGS_FILE), exist_ok=True)
    with open(GLOBAL_SETTINGS_FILE, 'w', encoding='utf-8') as file:
        json.dump(settings, file)

global_settings = load_global_settings()
LINES_PER_SCREEN = global_settings.get("lines_per_screen", 40)

def print_colored(text: str, color: str) -> None:
    colors: Dict[str, str] = {
        "green": "\033[92m",
        "red": "\033[91m",
        "blue": "\033[94m",
        "yellow": "\033[93m",
        "cyan": "\033[96m",
        "magenta": "\033[95m"
    }
    color_code: str = colors.get(color.lower(), "\033[0m")
    colored_text: str = f"{color_code}{text}\033[0m"
    print(colored_text)

def input_colored(prompt: str, color: str) -> str:
    colors: Dict[str, str] = {
        "green": "\033[92m",
        "red": "\033[91m",
        "blue": "\033[94m",
        "yellow": "\033[93m",
        "cyan": "\033[96m",
        "magenta": "\033[95m"
    }
    color_code: str = colors.get(color.lower(), "\033[0m")
    colored_prompt: str = f"{color_code}{prompt}\033[0m"
    return input(colored_prompt)

def read_epub_metadata(epub_path: str) -> Tuple[str, str, str, str]:
    with zipfile.ZipFile(epub_path, 'r') as epub:
        for file in epub.namelist():
            if 'content.opf' in file:
                with epub.open(file) as content_file:
                    content = content_file.read().decode('utf-8')
                    title_search = re.search(r'<dc:title[^>]*>(.*?)</dc:title>', content)
                    author_search = re.search(r'<dc:creator[^>]*>(.*?)</dc:creator>', content)
                    date_search = re.search(r'<dc:date[^>]*>(.*?)</dc:date>', content)
                    language_search = re.search(r'<dc:language[^>]*>(.*?)</dc:language>', content)
                    title = title_search.group(1) if title_search else 'Unknown Title'
                    author = author_search.group(1) if author_search else 'Unknown Author'
                    publication_date = date_search.group(1) if date_search else 'Unknown Date'
                    language = language_search.group(1) if language_search else 'Unknown Language'
                    return title, author, publication_date, language
    return 'Unknown Title', 'Unknown Author', 'Unknown Date', 'Unknown Language'

def read_epub_pages(epub_path: str) -> List[str]:
    pages = []
    with zipfile.ZipFile(epub_path, 'r') as epub:
        for file in sorted(epub.namelist()):
            if file.endswith(('.html', '.xhtml')):
                with epub.open(file) as html_file:
                    soup = BeautifulSoup(html_file.read(), 'html.parser')
                    text = soup.get_text(separator=' ')
                    text = re.sub(r'\s+', ' ', text).strip()
                    sentences = re.split(r'(?<=[.!?]) +', text)
                    cleaned_text = '\n\n'.join(sentences)
                    pages.append(cleaned_text)
    return pages

def get_epub_files_with_metadata(directory: str) -> List[Tuple[str, str, str, int, str, str]]:
    epub_files = [file for file in os.listdir(directory) if file.endswith('.epub')]
    epub_files_with_metadata = []

    for epub_file in epub_files:
        epub_path = os.path.join(directory, epub_file)
        title, author, date, language = read_epub_metadata(epub_path)
        with zipfile.ZipFile(epub_path, 'r') as epub:
            page_count = sum(1 for file in epub.namelist() if file.endswith(('.html', '.xhtml')))
        epub_files_with_metadata.append((epub_file, title, author, page_count, date, language))

    return epub_files_with_metadata

def display_choices(epub_files_with_metadata: List[Tuple[str, str, str, int, str, str]]) -> str:
    print_colored("Available EPUB files:", "blue")
    for index, (file, title, author, count, date, language) in enumerate(epub_files_with_metadata, start=1):
        print_colored(f"{index}. {title} by {author} ({count} pages, {date}, {language})", "green")
        print()  # Adding a blank line for spacing
    while True:
        choice = input_colored("Enter the number of the EPUB file you want to read: ", "yellow").strip()
        try:
            choice = int(choice)
            if 1 <= choice <= len(epub_files_with_metadata):
                break
            else:
                print_colored("Invalid choice. Please enter a number corresponding to the list.", "red")
        except ValueError:
            print_colored("Invalid input. Please enter a number.", "red")
    return epub_files_with_metadata[choice - 1][0]

def display_page(pages: List[str], page_number: int, line_offset: int = 0, lines_per_screen: int = 20) -> None:
    if 0 <= page_number < len(pages):
        os.system('clear' if os.name == 'posix' else 'cls')
        page_lines = pages[page_number].split('\n')
        total_lines = len(page_lines)
        start_line = line_offset
        end_line = min(start_line + lines_per_screen, total_lines)
        for line in page_lines[start_line:end_line]:
            print(line)
        progress = (start_line / total_lines) * 100 if total_lines else 100
        print_colored(f"\n{'-'*20} Page {page_number + 1} - {progress:.2f}% {'-'*20}\n", "cyan")
        print_colored(f"{book_title} by {book_author}", "magenta")  # Display current book

def save_page(pages: List[str], page_number: int, title: str, author: str) -> None:
    if 0 <= page_number < len(pages):
        filename = f"{title}_{author}_page_{page_number + 1}.txt"
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(pages[page_number])
        print_colored(f"Page {page_number + 1} saved as '{filename}'", "green")

def save_book(pages: List[str], title: str, author: str) -> None:
    filename = f"{title}_{author}.txt"
    with open(filename, 'w', encoding='utf-8') as file:
        for page in pages:
            file.write(page + '\n\n')
    print_colored(f"Book saved as '{filename}'", "green")

def search_text(pages: List[str], query: str) -> List[Tuple[int, str]]:
    results = []
    for i, page in enumerate(pages):
        matches = re.finditer(rf'[^.]*{re.escape(query)}[^.]*\.', page, re.IGNORECASE)
        for match in matches:
            results.append((i, match.group()))
    return results

def add_bookmark(bookmarks: List[Tuple[int, float]], page_number: int, progress: float) -> None:
    if (page_number, progress) not in bookmarks:
        bookmarks.append((page_number, progress))
        print_colored(f"Bookmark added on page {page_number + 1} at {progress:.2f}%", "green")
    else:
        print_colored(f"Bookmark already exists on page {page_number + 1} at {progress:.2f}%", "yellow")

def display_bookmarks(bookmarks: List[Tuple[int, float]]) -> None:
    if bookmarks:
        print_colored("Bookmarks:", "blue")
        for i, (page_number, progress) in enumerate(bookmarks):
            print_colored(f"{i + 1}. Page {page_number + 1} at {progress:.2f}%", "green")
    else:
        print_colored("No bookmarks added.", "yellow")

def jump_to_page(pages: List[str]) -> int:
    while True:
        try:
            page_input = input_colored("Enter the page number to jump to: ", "yellow").strip()
            page_number = int(page_input)
            if page_number < 1:
                print_colored("Invalid page number. Defaulting to page 1.", "red")
                return 0
            elif page_number > len(pages):
                print_colored(f"Invalid page number. The EPUB has {len(pages)} pages.", "red")
            else:
                return page_number - 1
        except ValueError:
            print_colored("Invalid input. Please enter a number.", "red")

def jump_to_percentage(pages: List[str]) -> Tuple[int, int]:
    while True:
        try:
            page_input = input_colored("Enter the page number: ", "yellow").strip()
            page_number = int(page_input)
            if page_number < 1:
                print_colored("Invalid page number. Defaulting to page 1.", "red")
                page_number = 0
            elif page_number > len(pages):
                print_colored(f"Invalid page number. The EPUB has {len(pages)} pages.", "red")
                continue
            else:
                page_number -= 1

            percentage_input = input_colored("Enter the percentage to jump to: ", "yellow").strip()
            percentage = float(percentage_input)
            if percentage < 0 or percentage > 100:
                print_colored("Invalid percentage. Please enter a value between 0 and 100.", "red")
                continue
            page_lines = pages[page_number].split('\n')
            total_lines = len(page_lines)
            line_offset = int((percentage / 100) * total_lines)
            return page_number, line_offset
        except ValueError:
            print_colored("Invalid input. Please enter a number.", "red")

def save_reading_session(book_id: str, page_number: int, line_offset: int, progress: float, bookmarks: List[Tuple[int, float]], search_history: List[str]) -> None:
    session_data = {
        "page_number": page_number,
        "line_offset": line_offset,
        "progress": progress,
        "bookmarks": bookmarks,
        "search_history": search_history
    }
    session_file = os.path.join(os.path.expanduser("~"), ".epub_reader", f"{book_id}.json")
    with open(session_file, 'w', encoding='utf-8') as file:
        json.dump(session_data, file)

def load_reading_session(book_id: str) -> Tuple[int, int, float, List[Tuple[int, float]], List[str]]:
    session_file = os.path.join(os.path.expanduser("~"), ".epub_reader", f"{book_id}.json")
    if os.path.exists(session_file):
        with open(session_file, 'r', encoding='utf-8') as file:
            session_data = json.load(file)
            return (
                session_data.get("page_number", 0),
                session_data.get("line_offset", 0),
                session_data.get("progress", 0.0),
                session_data.get("bookmarks", []),
                session_data.get("search_history", [])
            )
    return 0, 0, 0.0, [], []

def get_book_id(epub_path: str) -> str:
    return os.path.splitext(os.path.basename(epub_path))[0]

def adjust_lines_per_screen() -> None:
    global LINES_PER_SCREEN
    while True:
        try:
            lines_input = input_colored(f"Enter the number of lines to display per screen (current: {LINES_PER_SCREEN}): ", "yellow").strip()
            lines_per_screen = int(lines_input)
            if lines_per_screen < 1:
                print_colored("Invalid number. Please enter a value greater than 0.", "red")
                continue
            LINES_PER_SCREEN = lines_per_screen
            global_settings["lines_per_screen"] = LINES_PER_SCREEN
            save_global_settings(global_settings)
            print_colored(f"Lines per screen set to {LINES_PER_SCREEN}.", "green")
            break
        except ValueError:
            print_colored("Invalid input. Please enter a number.", "red")

def main() -> None:
    global book_title, book_author

    current_directory = os.getcwd()
    epub_files_with_metadata = get_epub_files_with_metadata(current_directory)

    if not epub_files_with_metadata:
        print_colored("No EPUB files found in the directory.", "red")
        return

    chosen_file = display_choices(epub_files_with_metadata)
    epub_path = os.path.join(current_directory, chosen_file)
    title, author, date, language = read_epub_metadata(epub_path)
    pages = read_epub_pages(epub_path)

    book_title, book_author = title, author

    book_id = get_book_id(epub_path)

    if not os.path.exists(os.path.expanduser("~/.epub_reader")):
        os.makedirs(os.path.expanduser("~/.epub_reader"))

    page_number, line_offset, progress, bookmarks, search_history = load_reading_session(book_id)

    display_page(pages, page_number, line_offset, lines_per_screen=LINES_PER_SCREEN)

    show_help = False

    while True:
        if show_help:
            command = input_colored("\n'n' for next page\n'p' for previous page\n'h' for help (this will hide all other commands)\n\nEnter your choice: ", "cyan").strip().lower()
        else:
            command = input_colored("\n'n' for next line\n'p' for previous line\n'h' for help (show all commands)\n\nEnter your choice: ", "cyan").strip().lower()
        
        if command == 'n':
            page_lines = pages[page_number].split('\n')
            if line_offset + LINES_PER_SCREEN < len(page_lines):
                line_offset += LINES_PER_SCREEN
            else:
                if page_number < len(pages) - 1:
                    page_number += 1
                    line_offset = 0
            display_page(pages, page_number, line_offset, lines_per_screen=LINES_PER_SCREEN)
        elif command == 'p':
            if line_offset > 0:
                line_offset -= LINES_PER_SCREEN
            else:
                if page_number > 0:
                    page_number -= 1
                    page_lines = pages[page_number].split('\n')
                    line_offset = max(0, len(page_lines) - LINES_PER_SCREEN)
            display_page(pages, page_number, line_offset, lines_per_screen=LINES_PER_SCREEN)
        elif command == 'h':
            if show_help:
                show_help = False
            else:
                print_colored("\nFull list of commands:\n\n"
                    "'n' for next line\n"
                    "'p' for previous line\n"
                    "'j' to jump to page\n"
                    "'jp' to jump to percentage\n"
                    "'b' to add bookmark\n"
                    "'bm' to view bookmarks\n"
                    "'jb' to jump to bookmark\n"
                    "'db' to delete bookmark\n"
                    "'dab' to delete all bookmarks\n"
                    "'s' to search\n"
                    "'sh' to view search history\n"
                    "'ds' to delete search history\n"
                    "'das' to delete all search history\n"
                    "'sp' to save page as text file\n"
                    "'sb' to save book as text file\n"
                    "'al' to adjust lines per screen\n"
                    "'q' to quit\n", "cyan")
                show_help = True
        # Other command handlers remain unchanged...
        elif command == 'j':
            page_number = jump_to_page(pages)
            line_offset = 0
            display_page(pages, page_number, line_offset, lines_per_screen=LINES_PER_SCREEN)
        elif command == 'jp':
            page_number, line_offset = jump_to_percentage(pages)
            display_page(pages, page_number, line_offset, lines_per_screen=LINES_PER_SCREEN)
        elif command == 'jb':
            if bookmarks:
                display_bookmarks(bookmarks)
                try:
                    bookmark_choice = int(input_colored("Enter the number of the bookmark to jump to: ", "yellow").strip()) - 1
                    if 0 <= bookmark_choice < len(bookmarks):
                        page_number, progress = bookmarks[bookmark_choice]
                        line_offset = int((progress / 100) * len(pages[page_number].split('\n')))
                        display_page(pages, page_number, line_offset, lines_per_screen=LINES_PER_SCREEN)
                    else:
                        print_colored("Invalid bookmark choice.", "red")
                except ValueError:
                    print_colored("Invalid input. Please enter a number.", "red")
            else:
                print_colored("No bookmarks available.", "yellow")
        elif command == 'db':
            if bookmarks:
                display_bookmarks(bookmarks)
                try:
                    bookmark_choice = int(input_colored("Enter the number of the bookmark to delete: ", "yellow").strip()) - 1
                    if 0 <= bookmark_choice < len(bookmarks):
                        del bookmarks[bookmark_choice]
                        print_colored("Bookmark deleted.", "green")
                    else:
                        print_colored("Invalid bookmark choice.", "red")
                except ValueError:
                    print_colored("Invalid input. Please enter a number.", "red")
            else:
                print_colored("No bookmarks available.", "yellow")
        elif command == 'dab':
            bookmarks.clear()
            print_colored("All bookmarks deleted.", "green")
        elif command == 'sh':
            if search_history:
                print_colored("Search History:", "blue")
                for i, query in enumerate(search_history):
                    print_colored(f"{i + 1}. {query}", "green")
            else:
                print_colored("No search history.", "yellow")
        elif command == 'ds':
            if search_history:
                print_colored("Search History:", "blue")
                for i, query in enumerate(search_history):
                    print_colored(f"{i + 1}. {query}", "green")
                try:
                    search_choice = int(input_colored("Enter the number of the search query to delete: ", "yellow").strip()) - 1
                    if 0 <= search_choice < len(search_history):
                        del search_history[search_choice]
                        print_colored("Search query deleted.", "green")
                    else:
                        print_colored("Invalid search query choice.", "red")
                except ValueError:
                    print_colored("Invalid input. Please enter a number.", "red")
            else:
                print_colored("No search history available.", "yellow")
        elif command == 'das':
            search_history.clear()
            print_colored("All search history deleted.", "green")
        elif command == 'al':
            adjust_lines_per_screen()
            page_lines = pages[page_number].split('\n')
            total_lines = len(page_lines)
            line_offset = int((progress / 100) * total_lines)
            display_page(pages, page_number, line_offset, lines_per_screen=LINES_PER_SCREEN)
        elif command == 'sp':
            save_page(pages, page_number, title, author)
        elif command == 'sb':
            save_book(pages, title, author)
        elif command == 'b':
            page_lines = pages[page_number].split('\n')
            progress = (line_offset / len(page_lines)) * 100 if len(page_lines) else 100
            add_bookmark(bookmarks, page_number, progress)
        elif command == 'bm':
            display_bookmarks(bookmarks)
        elif command == 's':
            query = input_colored("Enter text to search: ", "yellow")
            results = search_text(pages, query)
            search_history.append(query)
            if results:
                for i, sentence in results:
                    sentence = re.sub("\n", "", sentence)
                    print_colored(f"Page {i + 1}:\n{sentence}\n", "green")
            else:
                print_colored("No matches found.", "red")
        elif command == 'q':
            print_colored("\nExiting program.", "magenta")
            break
        else:
            print_colored("Invalid command. Please try again.", "red")

        page_lines = pages[page_number].split('\n')
        progress = (line_offset / len(page_lines)) * 100 if len(page_lines) else 100
        save_reading_session(book_id, page_number, line_offset, progress, bookmarks, search_history)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_colored("\nProgram exited gracefully.", "magenta")
