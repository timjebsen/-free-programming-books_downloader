 #! /bin/python3
import requests
import re
from pathlib import Path

# Get the md text
md_text = requests.get("https://raw.githubusercontent.com/EbookFoundation/free-programming-books/master/books/free-programming-books.md")
md_text = md_text.text

# Uncomment for local copy of the md
# with open("free-programming-books.md", "r") as f:
#     md_text = f.read()

# Remove newlines for easier regexing
md_text = md_text.replace("\n", "")

# Change "####" to "###" for easier regexing.
# This also makes all categories on the same level, ie. no sub cat's
md_text = md_text.replace("####", "###")

# Match each category
md_sections = re.findall(r"### (.*?)###", md_text)

# Specify which filetypes to download.
# Ignore websites, unknown files, html pages, git repos etc..
allowed_types = [
        'zip',
        'pdf', 
        'PDF', 
        'md', 
        # 'html' Saving html breaks links. 
        # TODO Implement save as link.
    ]

# Iterate through each section
for section in md_sections:
    # Section title. Used for dir name
    sect_name = re.findall(r"(.*?)\*", section)[0]

    # Book name and link
    book_name_link = re.findall(r"\* \[(.*?)\]\((.*?)\)", section)

    # Iterate through each book/link
    for book in book_name_link:
        book_type = re.findall(r".*\.(.*)", book[1])[0]
        book_name = book[0]
        book_link = book[1]

        # Only continue for accepted file types
        for allowed_type in allowed_types:
            if allowed_type in book_type:

                # Some filenames contain "/" breaking the dir path.
                book_name = book_name.replace("/", "-")

                print(book_name)
                print(book[1])

                # Build file dir path
                file_dir = "{}/{}.{}".format(sect_name, book_name,book_type)

                try:
                    # Check if the file already exists
                    f = open(file_dir)
                    f.close()

                except (IOError, FileNotFoundError):
                    try:
                        # It is unknown how large the files might be.
                        # Use the raw byte stream to safely handle large files.
                        # Ignore verify as some websites have faulty ssl certs
                        book_data = requests.get(book_link, stream=True, verify=False)

                        # Create new dir if doesnt exist
                        Path("{}".format(sect_name)).mkdir(parents=True, exist_ok=True)

                        # Create and write to the new file
                        with open(file_dir, "wb") as f:
                            for chunk in book_data.iter_content(2000):
                                f.write(chunk)

                    except FileNotFoundError:
                        # Sometimes the filename has unsupported characters which
                        # throws an error when trying to create the file.
                        # Ignore for time being.
                        # TODO handle above
                        print("Error saving file. File name probably contains bad characters")
                        print("Tried to save file: '{}'".format(file_dir))

                    except Exception as e:
                        # Handle unknown errors
                        print("Uknown error {}".format(e))
