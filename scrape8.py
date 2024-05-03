import requests
from bs4 import BeautifulSoup
import os
import logging
import urllib.parse
import xml.etree.ElementTree as ET
import xml.dom.minidom
import time
import random
import keyboard
from datetime import datetime

def setup_logging():
    # Configure logging
    logging.basicConfig(
        filename='script.log',  # Specify your log file path here
        filemode='a',  # Append mode
        format='%(asctime)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

def stuff_printer():
    print("Press 'Alt + p' for pause and 'Alt + z' for quit.")

def intro():
    print("Scraping has started..")

def finished():
    print("All images have been downloaded.")

def scrape_book_images(book_data):
    save_dir = "book_images"
    os.makedirs(save_dir, exist_ok=True)
    finished_controlnos = []

    # Input for minimum and maximum interval
    min_interval = int(input("Enter minimum interval (in seconds): ") or 3)
    max_interval = int(input("Enter maximum interval (in seconds): ") or 5)
    
    intro()

    for data in book_data:
        controlno = data['controlno']
        title = data['Title']
        query = '+'.join(title.split())
        search_url = f"https://www.google.com/search?tbm=isch&q={query}"

        # Check if image already exists
        image_filename = f"{controlno}.jpg"
        image_path = os.path.join(save_dir, image_filename)
        if os.path.exists(image_path):
            logging.info(f"Image for '{title}' with controlno '{controlno}' already exists, skipping...")
            continue

        try:
            response = requests.get(search_url)
            response.raise_for_status()  # Raise an exception for HTTP errors

            soup = BeautifulSoup(response.content, 'html.parser')
            image_urls = [img['src'] for img in soup.find_all('img') if img.get('src') and img['src'].startswith('http')]

            if image_urls:
                image_url = image_urls[0]
                image_data = requests.get(image_url).content
                if image_data:
                    with open(image_path, "wb") as img_file:
                        img_file.write(image_data)
                    logging.info(f"Downloaded image for '{title}' with controlno '{controlno}'")
                    finished_controlnos.append(controlno)
                else:
                    logging.warning(f"No valid image found for '{title}' with controlno '{controlno}'")
            else:
                logging.warning(f"No valid image found for '{title}' with controlno '{controlno}'")

        except requests.RequestException as e:
            logging.error(f"Failed to retrieve images for '{title}' with controlno '{controlno}': {e}")

        # Random interval
        interval = random.randint(min_interval, max_interval)
        logging.info(f"Waiting for {interval} seconds...")
        time.sleep(interval)

        # Check for pause or quit
        if keyboard.is_pressed('alt+p'):
            logging.info("Pausing...")
            while True:
                if keyboard.is_pressed('alt+p'):
                    logging.info("Resuming...")
                    break
                time.sleep(1)
        elif keyboard.is_pressed('alt+z'):
            logging.info("Stopping...")
            break

    finished()
        
    # Check if all files with the same name are already downloaded
    if len(os.listdir(save_dir)) == len(finished_controlnos):
        logging.info("All images have been downloaded.")
    else:
        logging.warning("Not all images have been downloaded.")

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

def main():
    setup_logging()  # Initialize logging

    # Print keypress instructions
    stuff_printer()

    # Example usage:
    xml_file = "tbl5FilesForTestBookControlNoTitleOnly.xml"
    book_data = parse_book_xml(xml_file)

    scrape_book_images(book_data)

if __name__ == "__main__":
    main()
