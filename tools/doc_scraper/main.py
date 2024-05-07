import argparse
import requests
from bs4 import BeautifulSoup
import html2text

def scrape_and_convert(url):
    # Send a GET request to the URL
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the primary content (you may need to adjust this based on the website structure)
        main_content = soup.find('div', class_='main-content')
        
        if main_content:
            # Convert the HTML content to Markdown
            converter = html2text.HTML2Text()
            markdown_content = converter.handle(str(main_content))
            
            # Prompt the user for the document name
            document_name = input("Enter the name for the Markdown document (without extension): ")
            
            # Save the Markdown content to a file
            with open(f"{document_name}.md", 'w', encoding='utf-8') as file:
                file.write(markdown_content)
            
            print(f"Markdown document '{document_name}.md' created successfully.")
        else:
            print("Primary content not found on the page.")
    else:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")

if __name__ == '__main__':
    # Create an argument parser
    parser = argparse.ArgumentParser(description='Scrape and convert a webpage to Markdown.')
    parser.add_argument('url', help='The URL of the webpage to scrape.')
    
    # Parse the command-line arguments
    args = parser.parse_args()
    
    # Call the scrape_and_convert function with the provided URL
    scrape_and_convert(args.url)
