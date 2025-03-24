#!/usr/bin/env python3
"""
Social Sharing Optimizer for OWL AI Agency Website

This script enhances the website's social sharing capabilities by:
1. Adding Open Graph and Twitter Card meta tags
2. Creating social share buttons with pre-populated content
3. Implementing LinkedIn article markup for professional sharing
"""

import os
from bs4 import BeautifulSoup
from colorama import Fore, Style, init

# Initialize colorama
init()

# Configuration
WEBSITE_ROOT = "../"
PAGES_TO_OPTIMIZE = [
    "index.html",
    "legal-research.html",
    "blog/index.html",
    "blog/legal-research-automation.html"
]

# Social media content templates
SOCIAL_CONTENT = {
    "index.html": {
        "title": "OWL AI Agency | Legal Research Automation for Law Firms",
        "description": "Transform your legal research with AI-powered automation. Reduce research time by up to 70% while improving accuracy and insights.",
        "image": "images/owl-ai-agency-social.jpg",
        "twitter_handle": "@OWL_AI_Agency"
    },
    "legal-research.html": {
        "title": "Legal Research Automation | OWL AI Agency",
        "description": "Our AI-powered legal research platform helps law firms find relevant precedents faster, analyze case law more effectively, and gain competitive advantages.",
        "image": "images/legal-research-automation-social.jpg",
        "twitter_handle": "@OWL_AI_Agency"
    },
    "blog/index.html": {
        "title": "Legal Technology Blog | OWL AI Agency",
        "description": "Expert insights on legal research automation, AI in law, and the future of legal technology from the OWL AI Agency team.",
        "image": "images/blog-social.jpg",
        "twitter_handle": "@OWL_AI_Agency"
    },
    "blog/legal-research-automation.html": {
        "title": "How Legal Research Automation Is Transforming Law Firms | OWL AI Agency",
        "description": "Discover how AI-powered legal research automation is helping law firms save time, reduce costs, and improve outcomes for their clients.",
        "image": "images/legal-research-automation-blog-social.jpg",
        "twitter_handle": "@OWL_AI_Agency"
    }
}

# Social share button HTML template
SHARE_BUTTONS_HTML = """
<div class="social-share-container">
  <h4>Share this page:</h4>
  <div class="social-share-buttons">
    <a href="https://www.linkedin.com/sharing/share-offsite/?url={url}" target="_blank" class="linkedin-share">
      <i class="fab fa-linkedin"></i>
    </a>
    <a href="https://twitter.com/intent/tweet?url={url}&text={text}&via={twitter_handle}" target="_blank" class="twitter-share">
      <i class="fab fa-twitter"></i>
    </a>
    <a href="https://www.facebook.com/sharer/sharer.php?u={url}" target="_blank" class="facebook-share">
      <i class="fab fa-facebook"></i>
    </a>
    <a href="mailto:?subject={subject}&body={body}" class="email-share">
      <i class="fas fa-envelope"></i>
    </a>
  </div>
</div>
"""

# CSS for social share buttons
SOCIAL_SHARE_CSS = """
.social-share-container {
  margin: 2rem 0;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 5px;
}

.social-share-container h4 {
  margin-top: 0;
  color: #333;
}

.social-share-buttons {
  display: flex;
  gap: 1rem;
}

.social-share-buttons a {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  color: white;
  transition: transform 0.2s ease;
}

.social-share-buttons a:hover {
  transform: scale(1.1);
}

.linkedin-share {
  background-color: #0077b5;
}

.twitter-share {
  background-color: #1da1f2;
}

.facebook-share {
  background-color: #3b5998;
}

.email-share {
  background-color: #6c757d;
}

.social-share-buttons i {
  font-size: 1.2rem;
}
"""


def add_open_graph_tags(soup, page_path, content):
    """Add Open Graph meta tags to the page."""
    head = soup.find('head')
    if not head:
        print(f"{Fore.RED}No head tag found in {page_path}{Style.RESET_ALL}")
        return False
    
    # Get the base URL
    base_url = "https://owl-ai-agency.com"
    page_rel_path = os.path.relpath(page_path, WEBSITE_ROOT).replace('\\', '/')
    page_url = f"{base_url}/{page_rel_path}"
    
    # Check if Open Graph tags already exist
    existing_og = soup.find('meta', property='og:title')
    if existing_og:
        print(f"{Fore.YELLOW}Open Graph tags already exist in {page_path}{Style.RESET_ALL}")
        return True
    
    # Create and add Open Graph meta tags
    og_tags = [
        ('property', 'og:title', content['title']),
        ('property', 'og:description', content['description']),
        ('property', 'og:image', f"{base_url}/{content['image']}"),
        ('property', 'og:url', page_url),
        ('property', 'og:type', 'website'),
        ('property', 'og:site_name', 'OWL AI Agency'),
        ('name', 'twitter:card', 'summary_large_image'),
        ('name', 'twitter:site', content['twitter_handle']),
        ('name', 'twitter:title', content['title']),
        ('name', 'twitter:description', content['description']),
        ('name', 'twitter:image', f"{base_url}/{content['image']}")
    ]
    
    for prop_type, prop_name, prop_content in og_tags:
        meta_tag = soup.new_tag('meta')
        meta_tag[prop_type] = prop_name
        meta_tag['content'] = prop_content
        head.append(meta_tag)
    
    print(f"{Fore.GREEN}Added Open Graph tags to {page_path}{Style.RESET_ALL}")
    return True


def add_social_share_buttons(soup, page_path, content):
    """Add social share buttons to the page."""
    # Find the main content area to add share buttons
    main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content')
    if not main_content:
        print(f"{Fore.RED}No suitable content area found in {page_path}{Style.RESET_ALL}")
        return False
    
    # Check if share buttons already exist
    if soup.find('div', class_='social-share-container'):
        print(f"{Fore.YELLOW}Social share buttons already exist in {page_path}{Style.RESET_ALL}")
        return True
    
    # Get the base URL and full page URL
    base_url = "https://owl-ai-agency.com"
    page_rel_path = os.path.relpath(page_path, WEBSITE_ROOT).replace('\\', '/')
    page_url = f"{base_url}/{page_rel_path}"
    
    # Format share text and URLs
    share_text = content['title']
    share_subject = content['title']
    share_body = f"{content['description']}\n\nRead more: {page_url}"
    
    # Format the share buttons HTML
    buttons_html = SHARE_BUTTONS_HTML.format(
        url=page_url,
        text=share_text,
        twitter_handle=content['twitter_handle'].replace('@', ''),
        subject=share_subject,
        body=share_body
    )
    
    # Add the buttons to the page
    buttons_soup = BeautifulSoup(buttons_html, 'html.parser')
    
    # Try to find a good position to insert the buttons
    target = main_content.find('h1') or main_content.find('h2')
    if target:
        # Insert after the heading
        target.insert_after(buttons_soup)
    else:
        # Append to the main content
        main_content.append(buttons_soup)
    
    print(f"{Fore.GREEN}Added social share buttons to {page_path}{Style.RESET_ALL}")
    return True


def add_social_share_css(soup, page_path):
    """Add CSS for social share buttons to the page."""
    head = soup.find('head')
    if not head:
        print(f"{Fore.RED}No head tag found in {page_path}{Style.RESET_ALL}")
        return False
    
    # Check if the CSS already exists
    for style in soup.find_all('style'):
        if '.social-share-container' in style.string:
            print(f"{Fore.YELLOW}Social share CSS already exists in {page_path}{Style.RESET_ALL}")
            return True
    
    # Add Font Awesome if not already included
    fa_link = soup.find('link', href=lambda href: href and 'font-awesome' in href)
    if not fa_link:
        fa_tag = soup.new_tag('link')
        fa_tag['rel'] = 'stylesheet'
        fa_tag['href'] = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css'
        head.append(fa_tag)
    
    # Create and add the style tag
    style_tag = soup.new_tag('style')
    style_tag.string = SOCIAL_SHARE_CSS
    head.append(style_tag)
    
    print(f"{Fore.GREEN}Added social share CSS to {page_path}{Style.RESET_ALL}")
    return True


def add_linkedin_article_markup(soup, page_path, content):
    """Add LinkedIn Article markup for professional sharing."""
    # Only add to blog posts
    if 'blog/' not in page_path:
        return True
    
    head = soup.find('head')
    if not head:
        return False
    
    # Check if LinkedIn article markup already exists
    if soup.find('meta', property='article:published_time'):
        print(f"{Fore.YELLOW}LinkedIn article markup already exists in {page_path}{Style.RESET_ALL}")
        return True
    
    # Add article-specific meta tags
    article_tags = [
        ('property', 'article:published_time', '2024-03-01T08:00:00+00:00'),
        ('property', 'article:author', 'https://www.linkedin.com/company/owl-ai-agency'),
        ('property', 'article:section', 'Legal Technology'),
        ('property', 'article:tag', 'Legal Research Automation'),
        ('property', 'article:tag', 'AI in Law'),
        ('property', 'article:tag', 'Legal Technology')
    ]
    
    for prop_type, prop_name, prop_content in article_tags:
        meta_tag = soup.new_tag('meta')
        meta_tag[prop_type] = prop_name
        meta_tag['content'] = prop_content
        head.append(meta_tag)
    
    print(f"{Fore.GREEN}Added LinkedIn article markup to {page_path}{Style.RESET_ALL}")
    return True


def optimize_page(page_name):
    """Optimize a single page for social sharing."""
    page_path = os.path.join(WEBSITE_ROOT, page_name)
    
    # Check if the page exists
    if not os.path.exists(page_path):
        print(f"{Fore.RED}Page not found: {page_path}{Style.RESET_ALL}")
        return False
    
    # Get content for this page
    if page_name not in SOCIAL_CONTENT:
        print(f"{Fore.RED}No social content defined for {page_name}{Style.RESET_ALL}")
        return False
    
    content = SOCIAL_CONTENT[page_name]
    
    try:
        # Read the HTML file
        with open(page_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Parse HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Add Open Graph and Twitter Card meta tags
        add_open_graph_tags(soup, page_path, content)
        
        # Add social share buttons
        add_social_share_buttons(soup, page_path, content)
        
        # Add CSS for social share buttons
        add_social_share_css(soup, page_path)
        
        # Add LinkedIn article markup for blog posts
        add_linkedin_article_markup(soup, page_path, content)
        
        # Write the modified HTML back to the file
        with open(page_path, 'w', encoding='utf-8') as f:
            f.write(str(soup))
        
        print(f"{Fore.GREEN}Successfully optimized {page_name} for social sharing{Style.RESET_ALL}")
        return True
        
    except Exception as e:
        print(f"{Fore.RED}Error optimizing {page_name}: {str(e)}{Style.RESET_ALL}")
        return False


def main():
    """Main function to optimize pages for social sharing."""
    print(f"{Fore.CYAN}===== OWL AI Agency Social Sharing Optimizer ====={Style.RESET_ALL}")
    
    success_count = 0
    for page in PAGES_TO_OPTIMIZE:
        print(f"\n{Fore.BLUE}Processing {page}...{Style.RESET_ALL}")
        if optimize_page(page):
            success_count += 1
    
    print(f"\n{Fore.GREEN}Social sharing optimization completed for {success_count}/{len(PAGES_TO_OPTIMIZE)} pages.{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Next steps:{Style.RESET_ALL}")
    print("1. Test social sharing on each page")
    print("2. Verify Open Graph tags using https://developers.facebook.com/tools/debug/")
    print("3. Verify Twitter Cards using https://cards-dev.twitter.com/validator")


if __name__ == "__main__":
    main()
