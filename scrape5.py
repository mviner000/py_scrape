import requests
from bs4 import BeautifulSoup
import os
import logging
import urllib.parse
import xml.etree.ElementTree as ET
import xml.dom.minidom

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Set the logging level to INFO
    format="%(asctime)s - %(levelname)s - %(message)s",  # Define the log message format
    datefmt="%Y-%m-%d %H:%M:%S"  # Define the date/time format
)

def scrape_book_images(book_data):
    # Create a directory to save downloaded images
    save_dir = "book_images"
    os.makedirs(save_dir, exist_ok=True)

    finished_controlnos = []  # List to store finished controlnos

    # Iterate over each book data
    for data in book_data:
        controlno = data['controlno']
        title = data['Title']

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
                        image_filename = f"{controlno}.jpg"  # Use controlno as filename
                        image_path = os.path.join(save_dir, image_filename)
                        with open(image_path, "wb") as img_file:
                            img_file.write(image_data)
                            logging.info(f"Downloaded image for '{title}' with controlno '{controlno}'")
                    else:
                        logging.warning(f"No image data retrieved for '{title}' with controlno '{controlno}'")
                except Exception as e:
                    logging.error(f"Failed to download image for '{title}' with controlno '{controlno}': {e}")
            else:
                logging.warning(f"No valid image found for '{title}' with controlno '{controlno}'")
        else:
            logging.error(f"Failed to retrieve images for '{title}' with controlno '{controlno}'")

        # Add finished controlno to the list
        finished_controlnos.append(controlno)

    # Write finished controlnos to a new XML file
    write_finished_controlnos(finished_controlnos)

def write_finished_controlnos(controlnos):
    # Create XML structure for finished controlnos
    root = ET.Element("FinishedControlNos")

    for controlno in controlnos:
        controlno_elem = ET.SubElement(root, "controlno")
        controlno_elem.text = str(controlno)

    # Create XML tree
    tree = ET.ElementTree(root)

    # Use xml.dom.minidom to format XML with new lines between elements
    xml_str = xml.dom.minidom.parseString(ET.tostring(root)).toprettyxml()

    # Write formatted XML to file
    with open("finishedscrape.xml", "w", encoding="utf-8") as xml_file:
        xml_file.write(xml_str)

def parse_book_xml(xml_file):
    # Parse the XML file
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Extract book data (controlno and Title) from the parsed XML
    book_data = []
    for cat in root.findall('tblCat'):
        controlno = cat.find('controlno').text
        title = cat.find('Title').text
        book_data.append({'controlno': controlno, 'Title': title})

    return book_data

# Example usage:
xml_file = "tbl5FilesForTestBookControlNoTitleOnly.xml"
book_data = parse_book_xml(xml_file)
scrape_book_images(book_data)
