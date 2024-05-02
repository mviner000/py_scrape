import requests
from bs4 import BeautifulSoup
import os
import logging
import urllib.parse
import xml.etree.ElementTree as ET
import xml.dom.minidom

# Configure logging
logging.basicConfig(
    filename='script.log',  # Log file path
    level=logging.INFO,  # Set the logging level to INFO
    format="%(asctime)s - %(levelname)s - %(message)s",  # Define the log message format
    datefmt="%Y-%m-%d %H:%M:%S"  # Define the date/time format
)

def scrape_book_images(book_data):
    save_dir = "book_images"
    os.makedirs(save_dir, exist_ok=True)
    finished_controlnos = []

    for data in book_data:
        controlno = data['controlno']
        title = data['Title']
        query = '+'.join(title.split())
        search_url = f"https://www.google.com/search?tbm=isch&q={query}"

        response = requests.get(search_url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            image_urls = [img['src'] for img in soup.find_all('img') if img.get('src') and img['src'].startswith('http')]

            if image_urls:
                image_url = image_urls[0]
                try:
                    image_data = requests.get(image_url).content
                    if image_data:
                        image_filename = f"{controlno}.jpg"
                        image_path = os.path.join(save_dir, image_filename)
                        with open(image_path, "wb") as img_file:
                            img_file.write(image_data)
                            logging.info(f"Downloaded image for '{title}' with controlno '{controlno}'")
                            finished_controlnos.append(controlno)
                except Exception as e:
                    logging.error(f"Failed to download image for '{title}' with controlno '{controlno}': {e}")
            else:
                logging.warning(f"No valid image found for '{title}' with controlno '{controlno}'")
        else:
            logging.error(f"Failed to retrieve images for '{title}' with controlno '{controlno}'")

        if finished_controlnos:
            log_last_processed_controlno(finished_controlnos[-1])

    write_finished_controlnos(finished_controlnos)

def write_finished_controlnos(controlnos):
    root = ET.Element("FinishedControlNos")

    for controlno in controlnos:
        controlno_elem = ET.SubElement(root, "controlno")
        controlno_elem.text = str(controlno)

    tree = ET.ElementTree(root)
    xml_str = xml.dom.minidom.parseString(ET.tostring(root)).toprettyxml()

    with open("finishedscrape.xml", "w", encoding="utf-8") as xml_file:
        xml_file.write(xml_str)

def log_last_processed_controlno(last_controlno):
    with open("last_processed_controlno.txt", "w") as checkpoint_file:
        checkpoint_file.write(str(last_controlno))

def parse_book_xml(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

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