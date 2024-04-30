import requests
from bs4 import BeautifulSoup
import os
import logging
import urllib.parse

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Set the logging level to INFO
    format="%(asctime)s - %(levelname)s - %(message)s",  # Define the log message format
    datefmt="%Y-%m-%d %H:%M:%S"  # Define the date/time format
)

def scrape_book_images(book_titles):
    # Create a directory to save downloaded images
    save_dir = "book_images"
    os.makedirs(save_dir, exist_ok=True)
    
    # Iterate over each book title
    for title in book_titles:
        # Construct the search query (replace spaces with '+')
        query = '+'.join(title.split())
        search_url = f"https://www.google.com/search?tbm=isch&q={query}"
        
        # Send a GET request to Google Images
        response = requests.get(search_url)
        
        if response.status_code == 200:
            # Parse the HTML content of the response
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract image URLs from the parsed content
            image_urls = [img['src'] for img in soup.find_all('img') if img.get('src') and img['src'].startswith('http')]
            
            # Download the first valid image (assuming it's the most relevant)
            if image_urls:
                image_url = image_urls[0]
                try:
                    # Validate and download the image
                    image_data = requests.get(image_url).content
                    if image_data:
                        image_filename = f"{title}.jpg"
                        image_path = os.path.join(save_dir, image_filename)
                        with open(image_path, "wb") as img_file:
                            img_file.write(image_data)
                            logging.info(f"Downloaded image for '{title}'")
                    else:
                        logging.warning(f"No image data retrieved for '{title}'")
                except Exception as e:
                    logging.error(f"Failed to download image for '{title}': {e}")
            else:
                logging.warning(f"No valid image found for '{title}'")
        else:
            logging.error(f"Failed to retrieve images for '{title}'")

# Example usage:
book_titles = ["Educational psychology", 
               "What does a Christian do Moral problems"]

scrape_book_images(book_titles)