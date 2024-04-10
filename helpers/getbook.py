import requests
from bs4 import BeautifulSoup
import os
import mimetypes
import time


def download_book(book_name, author_last_name):
    print(f"Searching for {book_name} by {author_last_name}")
    url = f"https://annas-archive.org/search?q={book_name}+{author_last_name}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    a_tags = soup.find_all('a')
    for a_tag in a_tags:
        href = a_tag.get('href')
        if href and '/md5/' in href:
            md5_id = href.split('/')[-1]
            book_url = f"http://libgen.li/ads.php?md5={md5_id}"
            print(f"Getting book at {book_url}")
            book_response = requests.get(book_url)
            book_soup = BeautifulSoup(book_response.text, 'html.parser')
            download_link_tag = book_soup.find('a', text='GET')
            if not download_link_tag:
                print(
                    f"Could not find a download link for {book_name} by {author_last_name}")
                return 0
            download_link = book_soup.find('a', text='GET').get('href')
            download_url = f"http://libgen.li/{download_link}"
            book_file = requests.get(download_url)
            mime_type = book_file.headers.get('content-type')
            filename = book_file.headers.get('content-disposition')
            if filename and filename[-1] == '"':
                filename = filename[:-1]
            extension = filename.split('.')[-1]
            if extension:
                filename = (f"./books/{book_name}.{extension}")
            else:
                # default to .pdf if we couldn't determine the extension
                print("Couldn't determine extension, defaulting to .epub")
                filename = f"{book_name}.epub"
            with open(filename, 'wb') as f:
                f.write(book_file.content)
            print(f"Downloaded {filename}")
            return 1  # Return 1 to increment the counter if a book was downloaded
    return 0  # Return 0 if no book was downloaded


start_time = time.time()  # Get the current time
download_count = 0  # Initialize a counter for the downloads

with open('books.txt', 'r') as file:
    for line in file:
        book_name, author_last_name = line.strip().split(',')
        # Increment the counter
        download_count += download_book(book_name, author_last_name)

end_time = time.time()  # Get the current time after the downloads

# Calculate the elapsed time and print the results
elapsed_time = end_time - start_time
print(f"Downloaded {download_count} files in {elapsed_time} seconds.")
