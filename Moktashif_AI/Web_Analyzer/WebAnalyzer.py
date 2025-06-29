from playwright.sync_api import sync_playwright
import json
from datetime import datetime
from typing import Dict, List
import logging
import os
from urllib.parse import urljoin,urlparse


# File structre:
#     1. Class WebAnalyzer:
#         1. def __init__ (self, url: str)
#         2. def setup_logging(self) - initializes and configures Python built-in logging system for the WebAnalyzer class
#         3. def ensure_output_directory(self) - Create output directory if it doesn't exist 
#         4. def analyze_page(self) -> Dict - Main function to analyze the webpage
#         5. def perform_basic_analysis(self, page) -> Dict - Perform the basic page analysis
#         6. def analyze_elements(self, page) -> Dict - Analyze basic elements on the page
#         7. def analyze_structure(self, page) -> Dict - Analyze the page structure
#         8. def analyze_functionality(self, page) -> Dict - Analyze page functionality
#         9. def analyze_forms(self, page) -> Dict - Analyze forms on the page
#         10. def analyze_inputs(self, page) -> Dict - Analyze input elements on the page
#         11. def gather_extended_info(self, page, context, response_headers) -> Dict - Gather extended information about the page
#         12. def extract_links(self, page) -> List[Dict] - Extract all links from the page with additional context  
#         13. def save_extended_info(self, extended_info: Dict) - Save extended information to separate files 
#         14. def format_links_for_text(self, links: List[Dict]) -> str - Format links for text output 
#         15. def format_cookies_for_text(self, cookies: List[Dict]) -> str - Format cookies for text output
        
    
class WebAnalyzer:
    def __init__ (self, url: str):
        self.url = url
        self.setup_logging()
        self.output_dir = "web_analysis_output"
        self.ensure_output_directory()
    
    # initializes and configures Python built-in logging system for the WebAnalyzer class
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    # Create output directory if it doesn't exist     
    def ensure_output_directory(self):
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    # Main function to analyze the webpage
    def analyze_page(self) -> Dict:
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context()
                page = context.new_page()
                
                self.logger.info(f"Navigating to {self.url}")
                try:
                    response = page.goto(self.url, wait_until="networkidle", timeout=30000)
                    if not response:
                        raise Exception("Failed to load page")
                    if response.status >= 400:
                        raise Exception(f"Page returned status code {response.status}")
                    response_headers = response.headers
                except Exception as e:
                    self.logger.error(f"Navigation failed: {str(e)}")
                    raise
                page.wait_for_load_state("networkidle")
                analysis_result = self.perform_basic_analysis(page)
                extended_info = self.gather_extended_info(page, context, response_headers)
                self.save_extended_info(extended_info)
                
                context.close()
                browser.close()
                return analysis_result,extended_info
        except Exception as e:
            self.logger.error(f"Error analyzing page: {str(e)}")
            raise
            
    # Perform the basic page analysis        
    def perform_basic_analysis(self, page) -> Dict:
        return{
            "url": self.url,
            "timestamp": datetime.now().isocalendar(),
            "title": page.title(),
            "elements": self.analyze_elements(page),
            "structure": self.analyze_structure(page),
            "functionality": self.analyze_functionality(page),
            "inputs": self.analyze_inputs(page)
        }
        
    # Analyze basic elements on the page    
    def analyze_elements(self, page) -> Dict:
        try:
            return {
                "forms": len(page.query_selector_all("form")),
                "buttons": len(page.query_selector_all("button")),
                "links": len(page.query_selector_all("a")),
                "images": len(page.query_selector_all("img")),
                "inputs": len(page.query_selector_all("input")),
                "headings": {
                    "h1": len(page.query_selector_all("h1")),
                    "h2": len(page.query_selector_all("h2")),
                    "h3": len(page.query_selector_all("h3"))
                },
                "lists": {
                    "ul": len(page.query_selector_all("ul")),
                    "ol": len(page.query_selector_all("ol"))
                },
                "tables": len(page.query_selector_all("table")),
                "iframes": len(page.query_selector_all("iframe"))
            }
        except Exception as e:
            self.logger.error(f"Error analyzing elements: {str(e)}")
            return {}
        
        
    # Analyze the page structure
    def analyze_structure(self, page) -> Dict:
        try:
            return {
                "has_header": bool(page.query_selector("header")),
                "has_footer": bool(page.query_selector("footer")),
                "has_nav": bool(page.query_selector("nav")),
                "has_main": bool(page.query_selector("main")),
                "has_aside": bool(page.query_selector("aside")),
                "has_article": bool(page.query_selector("article")),
                "meta_tags": len(page.query_selector_all("meta")),
                "scripts": {
                    "total": len(page.query_selector_all("script")),
                    "external": len(page.query_selector_all("script[src]"))
                },
                "stylesheets": {
                    "total": len(page.query_selector_all("link[rel='stylesheet']")),
                    "internal": len(page.query_selector_all("style"))
                }
            }
        except Exception as e:
            self.logger.error(f"Error analyzing structure: {str(e)}")
            return {}
        
        
        
    # Analyze page functionality    
    def analyze_functionality(self, page) -> Dict:
        try:
            return {
                "interactive_elements": {
                    "clickable": len(page.query_selector_all("[onclick], [role='button']")),
                    "hoverable": len(page.query_selector_all("[onmouseover], [onmouseenter]")),
                    "keyboard": len(page.query_selector_all("[onkeyup], [onkeydown], [onkeypress]"))
                },
                "forms_analysis": self.analyze_forms(page),
                "media_elements": {
                    "video": len(page.query_selector_all("video")),
                    "audio": len(page.query_selector_all("audio")),
                    "canvas": len(page.query_selector_all("canvas")),
                    "svg": len(page.query_selector_all("svg"))
                }
            }
        except Exception as e:
            self.logger.error(f"Error analyzing functionality: {str(e)}")
            return {}
        
        
        
    # Analyze forms on the page    
    def analyze_forms(self, page) -> Dict:
        try:
            forms = page.query_selector_all("form")
            forms_analysis = []

            for form in forms:
                form_info = {
                    "action": form.get_attribute("action"),
                    "method": form.get_attribute("method"),
                    "inputs": len(form.query_selector_all("input")),
                    "required_fields": len(form.query_selector_all("[required]")),
                    "submit_buttons": len(form.query_selector_all("button[type='submit'], input[type='submit']"))
                }
                forms_analysis.append(form_info)

            return {
                "total_forms": len(forms),
                "forms_details": forms_analysis
            }
        except Exception as e:
            self.logger.error(f"Error analyzing forms: {str(e)}")
            return {}




    # Analyze input elements on the page    
    def analyze_inputs(self, page) -> Dict:
        try:
            inputs = page.query_selector_all("input")
            input_types = {}

            for input_elem in inputs:
                input_type = input_elem.get_attribute("type") or "text"
                input_types[input_type] = input_types.get(input_type, 0) + 1

            return {
                "total": len(inputs),
                "types": input_types,
                "required": len(page.query_selector_all("input[required]")),
                "with_placeholder": len(page.query_selector_all("input[placeholder]")),
                "with_pattern": len(page.query_selector_all("input[pattern]")),
                "with_validation": len(
                    page.query_selector_all("input[minlength], input[maxlength], input[min], input[max]"))
            }
        except Exception as e:
            self.logger.error(f"Error analyzing inputs: {str(e)}")
            return {}
        
        
        
        
    # Gather extended information about the page    
    def gather_extended_info(self, page, context, response_headers) -> Dict:
        try:
            links = self.extract_links(page)
            page_source = page.content()
            cookies = context.cookies()

            meta_headers = page.evaluate("""() => {
                let headers = {};
                for (let header of document.getElementsByTagName('meta')) {
                    if (header.name) {
                        headers[header.name] = header.content;
                    }
                }
                return headers;
            }""")

            return {
                "url": self.url,
                "links": links,
                "page_source": page_source,
                "cookies": cookies,
                "meta_headers": meta_headers,
                "response_headers": response_headers,  # Include response headers here
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            self.logger.error(f"Error gathering extended info: {str(e)}")
            return {}
        
        
        
        
    # Extract all links from the page with additional context    
    def extract_links(self, page) -> List[Dict]:
        links = []
        try:
            for link in page.query_selector_all("a"):
                href = link.get_attribute("href")
                if href:
                    if not href.startswith(("http://", "https://", "mailto:", "tel:", "#")):
                        href = urljoin(self.url, href)
                    links.append({
                        "url": href,
                        "text": link.inner_text().strip(),
                        "title": link.get_attribute("title") or "",
                        "type": "internal" if self.url in href else "external"
                    })
        except Exception as e:
            self.logger.error(f"Error extracting links: {str(e)}")
        return links
    
    
    
    
    # Save extended information to separate files    
    def save_extended_info(self, extended_info: Dict):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Create detailed information file
        detailed_info = {
            "url": extended_info["url"],
            "timestamp": extended_info["timestamp"],
            "analysis": {
                "links": {
                    "total_count": len(extended_info["links"]),
                    "internal_count": sum(1 for link in extended_info["links"] if link["type"] == "internal"),
                    "external_count": sum(1 for link in extended_info["links"] if link["type"] == "external"),
                    "all_links": extended_info["links"]
                },
                "cookies": {
                    "count": len(extended_info["cookies"]),
                    "details": extended_info["cookies"]
                },
                "meta_headers": extended_info["meta_headers"],
                "response_headers": extended_info["response_headers"]
            }
        }
        parsed_url = urlparse(extended_info["url"])
        path_name = parsed_url.path.rstrip('/').split('/')[-1]
        domain_name = f"{parsed_url.scheme}://{parsed_url.netloc}"

        outer = timestamp
        if path_name == "":
            outer = "Home"
        else:
            outer = path_name

        # Save detailed analysis
        with open(os.path.join(self.output_dir, f"detailed_analysis_{outer}_{timestamp}.json"), "w", encoding='utf-8') as f:
            json.dump(detailed_info, f, indent=4, ensure_ascii=False)

        # Save page source
        with open(os.path.join(self.output_dir, f"page_source_{outer}_{timestamp}.html"), "w", encoding='utf-8') as f:
            f.write(extended_info["page_source"])

        # Save links in a readable format
        links_text = self.format_links_for_text(extended_info["links"])
        with open(os.path.join(self.output_dir, f"extracted_links_{outer}_{timestamp}.txt"), "w", encoding='utf-8') as f:
            f.write(links_text)

        # Save cookies in a readable format
        cookies_text = self.format_cookies_for_text(extended_info["cookies"])
        with open(os.path.join(self.output_dir, f"cookies_{outer}_{timestamp}.txt"), "w", encoding='utf-8') as f:
            f.write(cookies_text)
            
            
            
            
            
    # Format links for text output    
    def format_links_for_text(self, links: List[Dict]) -> str:
        output = "Extracted Links Report\n"
        output += "===================\n\n"

        # Group links by type
        internal_links = [link for link in links if link["type"] == "internal"]
        external_links = [link for link in links if link["type"] == "external"]

        output += f"Total Links Found: {len(links)}\n"
        output += f"Internal Links: {len(internal_links)}\n"
        output += f"External Links: {len(external_links)}\n\n"

        output += "Internal Links:\n"
        output += "--------------\n"
        for link in internal_links:
            output += f"URL: {link['url']}\n"
            output += f"Text: {link['text']}\n"
            if link['title']:
                output += f"Title: {link['title']}\n"
            output += "\n"

        output += "External Links:\n"
        output += "--------------\n"
        for link in external_links:
            output += f"URL: {link['url']}\n"
            output += f"Text: {link['text']}\n"
            if link['title']:
                output += f"Title: {link['title']}\n"
            output += "\n"

        return output






    # Format cookies for text output
    def format_cookies_for_text(self, cookies: List[Dict]) -> str:
        output = "Cookies Report\n"
        output += "=============\n\n"

        output += f"Total Cookies Found: {len(cookies)}\n\n"

        for cookie in cookies:
            output += f"Name: {cookie.get('name', 'N/A')}\n"
            output += f"Domain: {cookie.get('domain', 'N/A')}\n"
            output += f"Path: {cookie.get('path', 'N/A')}\n"
            output += f"Secure: {cookie.get('secure', False)}\n"
            output += f"HTTP Only: {cookie.get('httpOnly', False)}\n"
            output += f"Same Site: {cookie.get('sameSite', 'N/A')}\n"
            output += f"Expires: {cookie.get('expires', 'Session')}\n"
            output += "-" * 50 + "\n"

        return output
