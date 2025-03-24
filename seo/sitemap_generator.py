import datetime
import xml.dom.minidom
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin, urlparse


# Constants
BASE_URL = "https://owl-ai-agency.com"
WEBSITE_ROOT = "../"  # Path to the website root directory
OUTPUT_FILE = "../sitemap.xml"
IMAGE_SITEMAP_FILE = "../image-sitemap.xml"
SITEMAP_INDEX_FILE = "../sitemap-index.xml"
EXCLUDED_EXTENSIONS = [
    '.css', '.js', '.jpg', '.jpeg', '.png', '.gif', '.pdf', '.ico'
]
INCLUDED_EXTENSIONS = [
    '.html', '.htm', ''  # Empty string to include directory index files
]
EXCLUDED_DIRECTORIES = [
    '.git', 'node_modules', 'seo', '__pycache__'
]
CHANGE_FREQ = {
    'index.html': 'weekly',
    'blog': 'weekly',
    'legal-research.html': 'monthly',
    'about.html': 'monthly',
    'contact.html': 'monthly',
    'default': 'monthly'
}
PRIORITY = {
    'index.html': '1.0',
    'blog': '0.8',
    'legal-research.html': '0.9',
    'about.html': '0.7',
    'contact.html': '0.7',
    'default': '0.5'
}
# International SEO settings - add languages you want to support
HREFLANG_SUPPORT = {
    'en': BASE_URL,  # English (default)
    'zh': f"{BASE_URL}/zh",  # Chinese
    'es': f"{BASE_URL}/es",  # Spanish
}


def get_all_pages_local():
    """
    Scan the local website directory and get all HTML pages.

    Returns:
        tuple: A list of all discovered URLs and a dictionary of images by URL
    """
    pages = []
    images = {}  # Dictionary to store images for each page
    
    # Walk through the website directory
    for root, dirs, files in os.walk(WEBSITE_ROOT):
        # Skip excluded directories
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRECTORIES]
        
        for file in files:
            # Check if the file is an HTML file or other important website file
            _, ext = os.path.splitext(file)
            if ext.lower() in INCLUDED_EXTENSIONS or file in ['robots.txt', 'sitemap.xml']:
                # Get the relative path from the website root
                rel_path = os.path.relpath(os.path.join(root, file), WEBSITE_ROOT)
                # Convert Windows path separators to URL format
                rel_path = rel_path.replace('\\', '/')
                
                # Skip files in excluded directories (deeper check)
                if any(excluded_dir in rel_path for excluded_dir in EXCLUDED_DIRECTORIES):
                    continue
                
                # Handle index.html files
                if file.lower() == 'index.html':
                    rel_dir = os.path.dirname(rel_path)
                    if rel_dir:
                        url_path = f"{rel_dir}/"
                    else:
                        url_path = ""
                else:
                    url_path = rel_path
                
                # Create the full URL
                page_url = f"{BASE_URL}/{url_path}"
                pages.append(page_url)
                
                # Parse the HTML file to find images
                if ext.lower() in ['.html', '.htm']:
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            soup = BeautifulSoup(content, 'html.parser')
                            
                            # Find all images on the page
                            page_images = []
                            for img in soup.find_all('img', src=True):
                                img_src = img['src']
                                # Skip external images
                                if img_src.startswith(('http://', 'https://')):
                                    continue
                                    
                                # Convert relative image path to URL
                                img_url = f"{BASE_URL}/{img_src.lstrip('/')}"
                                
                                img_data = {
                                    'loc': img_url,
                                    'title': img.get('alt', '') or img.get('title', '') or os.path.basename(img_src)
                                }
                                page_images.append(img_data)
                            
                            if page_images:
                                images[page_url] = page_images
                    except Exception as e:
                        print(f"Error processing {file_path}: {e}")
    
    return pages, images


def create_sitemap(urls, output_file, images=None):
    """
    Create a sitemap XML file from the list of URLs.

    Args:
        urls (list): List of URLs to include in the sitemap
        output_file (str): Path to the output sitemap file
        images (dict, optional): Dictionary of images by URL
    """
    # Create the XML document
    doc = xml.dom.minidom.getDOMImplementation().createDocument(
        None, "urlset", None
    )
    root = doc.documentElement
    root.setAttribute("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")
    root.setAttribute("xmlns:xhtml", "http://www.w3.org/1999/xhtml")
    
    # Add image namespace if we have images
    if images:
        root.setAttribute("xmlns:image", "http://www.google.com/schemas/sitemap-image/1.1")

    # Get the current date in the required format
    today = datetime.datetime.now().strftime("%Y-%m-%d")

    # Add each URL to the sitemap
    for url in urls:
        url_element = doc.createElement("url")

        # Add location
        loc = doc.createElement("loc")
        loc_text = doc.createTextNode(url)
        loc.appendChild(loc_text)
        url_element.appendChild(loc)

        # Add last modified date
        lastmod = doc.createElement("lastmod")
        lastmod_text = doc.createTextNode(today)
        lastmod.appendChild(lastmod_text)
        url_element.appendChild(lastmod)

        # Add change frequency
        changefreq = doc.createElement("changefreq")
        # Determine the appropriate change frequency based on the URL
        freq = CHANGE_FREQ['default']
        for key in CHANGE_FREQ:
            if key in url:
                freq = CHANGE_FREQ[key]
                break
        changefreq_text = doc.createTextNode(freq)
        changefreq.appendChild(changefreq_text)
        url_element.appendChild(changefreq)

        # Add priority
        priority = doc.createElement("priority")
        # Determine the appropriate priority based on the URL
        pri = PRIORITY['default']
        for key in PRIORITY:
            if key in url:
                pri = PRIORITY[key]
                break
        priority_text = doc.createTextNode(pri)
        priority.appendChild(priority_text)
        url_element.appendChild(priority)
        
        # Add hreflang tags for international SEO
        for lang, lang_url_base in HREFLANG_SUPPORT.items():
            # Create the alternate URL for this language
            if lang == 'en':  # Default language
                alternate_url = url
            else:
                # Replace the base URL with the language-specific base URL
                alternate_url = url.replace(BASE_URL, lang_url_base)
            
            alternate = doc.createElement("xhtml:link")
            alternate.setAttribute("rel", "alternate")
            alternate.setAttribute("hreflang", lang)
            alternate.setAttribute("href", alternate_url)
            url_element.appendChild(alternate)
        
        # Add images if available for this URL
        if images and url in images:
            for img_data in images[url]:
                img_element = doc.createElement("image:image")
                
                img_loc = doc.createElement("image:loc")
                img_loc_text = doc.createTextNode(img_data['loc'])
                img_loc.appendChild(img_loc_text)
                img_element.appendChild(img_loc)
                
                if img_data['title']:
                    img_title = doc.createElement("image:title")
                    img_title_text = doc.createTextNode(img_data['title'])
                    img_title.appendChild(img_title_text)
                    img_element.appendChild(img_title)
                
                url_element.appendChild(img_element)

        root.appendChild(url_element)

    # Write the XML to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(doc.toprettyxml(indent="  "))


def create_image_sitemap(images, output_file):
    """
    Create a dedicated image sitemap XML file.

    Args:
        images (dict): Dictionary of images by URL
        output_file (str): Path to the output image sitemap file
    """
    # Create the XML document
    doc = xml.dom.minidom.getDOMImplementation().createDocument(
        None, "urlset", None
    )
    root = doc.documentElement
    root.setAttribute("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")
    root.setAttribute("xmlns:image", "http://www.google.com/schemas/sitemap-image/1.1")

    # Add each URL with images to the sitemap
    for url, img_list in images.items():
        url_element = doc.createElement("url")

        # Add location
        loc = doc.createElement("loc")
        loc_text = doc.createTextNode(url)
        loc.appendChild(loc_text)
        url_element.appendChild(loc)

        # Add each image
        for img_data in img_list:
            img_element = doc.createElement("image:image")
            
            img_loc = doc.createElement("image:loc")
            img_loc_text = doc.createTextNode(img_data['loc'])
            img_loc.appendChild(img_loc_text)
            img_element.appendChild(img_loc)
            
            if img_data['title']:
                img_title = doc.createElement("image:title")
                img_title_text = doc.createTextNode(img_data['title'])
                img_title.appendChild(img_title_text)
                img_element.appendChild(img_title)
            
            url_element.appendChild(img_element)

        root.appendChild(url_element)

    # Write the XML to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(doc.toprettyxml(indent="  "))


def create_sitemap_index(sitemap_files, output_file=SITEMAP_INDEX_FILE):
    """
    Create a sitemap index file that references multiple sitemaps.

    Args:
        sitemap_files (list): List of sitemap files to include
        output_file (str): Path to the output sitemap index file
    """
    # Create the XML document
    doc = xml.dom.minidom.getDOMImplementation().createDocument(
        None, "sitemapindex", None
    )
    root = doc.documentElement
    root.setAttribute("xmlns", "http://www.sitemaps.org/schemas/sitemap/0.9")

    # Get the current date in the required format
    today = datetime.datetime.now().strftime("%Y-%m-%d")

    # Add each sitemap to the index
    for sitemap_file in sitemap_files:
        # Convert local file path to URL
        sitemap_url = f"{BASE_URL}/{os.path.basename(sitemap_file)}"
        
        sitemap_element = doc.createElement("sitemap")
        
        # Add location
        loc = doc.createElement("loc")
        loc_text = doc.createTextNode(sitemap_url)
        loc.appendChild(loc_text)
        sitemap_element.appendChild(loc)
        
        # Add last modified date
        lastmod = doc.createElement("lastmod")
        lastmod_text = doc.createTextNode(today)
        lastmod.appendChild(lastmod_text)
        sitemap_element.appendChild(lastmod)
        
        root.appendChild(sitemap_element)

    # Write the XML to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(doc.toprettyxml(indent="  "))


def main():
    """Main function to generate the sitemap."""
    print(f"Starting sitemap generation for {BASE_URL}")
    
    # Get all pages and images
    pages, images = get_all_pages_local()
    
    print(f"Found {len(pages)} pages and {sum(len(imgs) for imgs in images.values())} images")
    
    # Create the main sitemap
    create_sitemap(pages, OUTPUT_FILE, images)
    print(f"Main sitemap created at {OUTPUT_FILE}")
    
    # Create the image sitemap if there are images
    if images:
        create_image_sitemap(images, IMAGE_SITEMAP_FILE)
        print(f"Image sitemap created at {IMAGE_SITEMAP_FILE}")
    
    # Create the sitemap index
    sitemap_files = [OUTPUT_FILE]
    if images:
        sitemap_files.append(IMAGE_SITEMAP_FILE)
    
    create_sitemap_index(sitemap_files)
    print(f"Sitemap index created at {SITEMAP_INDEX_FILE}")


if __name__ == "__main__":
    main()
