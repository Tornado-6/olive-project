import requests
from bs4 import BeautifulSoup
import re
import json
import cssutils
import logging
from urllib.parse import urljoin, urlparse
from pathlib import Path
import os

class WebsiteStyleExtractor:
    def __init__(self, url):
        self.url = url
        self.base_url = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        cssutils.log.setLevel(logging.CRITICAL)  # Suppress cssutils warnings

    def get_page_content(self):
        """Fetch the webpage content"""
        try:
            response = self.session.get(self.url)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching page: {e}")
            return None

    def extract_inline_styles(self, soup):
        """Extract inline styles from style tags"""
        inline_styles = []
        for style in soup.find_all('style'):
            if style.string:
                inline_styles.append(style.string)
        return inline_styles

    def extract_external_stylesheets(self, soup):
        """Extract and download external stylesheets"""
        external_styles = []
        for link in soup.find_all('link', rel='stylesheet'):
            href = link.get('href')
            if href:
                full_url = urljoin(self.base_url, href)
                try:
                    response = self.session.get(full_url)
                    response.raise_for_status()
                    external_styles.append(response.text)
                except requests.RequestException as e:
                    print(f"Error fetching stylesheet {full_url}: {e}")
        return external_styles

    def extract_colors(self, css_content):
        """Extract color values from CSS"""
        color_pattern = r'#[0-9a-fA-F]{3,6}|rgb\([^)]+\)|rgba\([^)]+\)|hsl\([^)]+\)|hsla\([^)]+\)'
        colors = re.findall(color_pattern, css_content)
        return list(set(colors))

    def extract_fonts(self, css_content):
        """Extract font families from CSS"""
        font_pattern = r'font-family:\s*([^;}]+)'
        fonts = re.findall(font_pattern, css_content)
        return list(set(fonts))

    def extract_dimensions(self, css_content):
        """Extract common dimensions and spacing values"""
        dimension_pattern = r':\s*(-?\d+(?:\.\d+)?(?:px|em|rem|%|vh|vw))'
        dimensions = re.findall(dimension_pattern, css_content)
        return list(set(dimensions))

    def extract_media_queries(self, css_content):
        """Extract media queries"""
        media_pattern = r'@media[^{]+\{[^}]+\}'
        media_queries = re.findall(media_pattern, css_content)
        return media_queries

    def parse_css_rules(self, css_content):
        """Parse CSS content into structured rules"""
        sheet = cssutils.parseString(css_content)
        rules = []
        
        for rule in sheet:
            if rule.type == rule.STYLE_RULE:
                rules.append({
                    'selector': rule.selectorText,
                    'styles': {p.name: p.value for p in rule.style}
                })
            elif rule.type == rule.MEDIA_RULE:
                rules.append({
                    'media': rule.media.mediaText,
                    'rules': [{'selector': r.selectorText, 
                              'styles': {p.name: p.value for p in r.style}} 
                             for r in rule]
                })
        
        return rules

    def extract_all_styles(self):
        """Extract all styles and design elements from the website"""
        content = self.get_page_content()
        if not content:
            return None

        soup = BeautifulSoup(content, 'html.parser')
        
        # Collect all CSS content
        css_content = '\n'.join(
            self.extract_inline_styles(soup) +
            self.extract_external_stylesheets(soup)
        )

        # Extract design elements
        design_elements = {
            'colors': self.extract_colors(css_content),
            'fonts': self.extract_fonts(css_content),
            'dimensions': self.extract_dimensions(css_content),
            'media_queries': self.extract_media_queries(css_content),
            'css_rules': self.parse_css_rules(css_content)
        }

        return design_elements

    def save_to_json(self, output_dir='website_styles'):
        """Save extracted styles to JSON file"""
        styles = self.extract_all_styles()
        if not styles:
            return

        # Create output directory if it doesn't exist
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        # Save to JSON file
        output_file = os.path.join(output_dir, 'styles.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(styles, f, indent=2)
        
        print(f"Styles saved to {output_file}")

    def generate_css_file(self, output_dir='website_styles'):
        """Generate a CSS file from extracted styles"""
        styles = self.extract_all_styles()
        if not styles:
            return

        Path(output_dir).mkdir(parents=True, exist_ok=True)
        output_file = os.path.join(output_dir, 'styles.css')

        with open(output_file, 'w', encoding='utf-8') as f:
            # Write CSS custom properties (variables)
            f.write(':root {\n')
            for i, color in enumerate(styles['colors']):
                f.write(f'  --color-{i + 1}: {color};\n')
            f.write('}\n\n')

            # Write regular CSS rules
            for rule in styles['css_rules']:
                if isinstance(rule, dict):
                    if 'media' in rule:
                        # Write media query
                        f.write('@media ' + rule['media'] + ' {\n')
                        for subrule in rule['rules']:
                            f.write('  ' + subrule['selector'] + ' {\n')
                            for prop, value in subrule['styles'].items():
                                f.write(f'    {prop}: {value};\n')
                            f.write('  }\n')
                        f.write('}\n\n')
                    else:
                        # Write regular rule
                        f.write(rule['selector'] + ' {\n')
                        for prop, value in rule['styles'].items():
                            f.write(f'  {prop}: {value};\n')
                        f.write('}\n\n')

        print(f"CSS file generated at {output_file}")

def main():
    # Extract styles from oliveworld.co.in
    extractor = WebsiteStyleExtractor('https://www.oliveworld.co.in')
    
    # Save both JSON and CSS versions
    extractor.save_to_json()
    extractor.generate_css_file()

if __name__ == '__main__':
    main()
