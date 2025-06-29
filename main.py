import argparse
import time
from Utils.logger import Logger
import os, sys
from Web_Analyzer import WebAnalyzer
from urllib.parse import urlparse
from Utils import Agents
from Prompts import prompts
import json
import subprocess

Final_Data = []        # Accumulates tuples of (page_name, basic_analysis, extended_info) for each page
Final_Result = []      # Stores the final exploit outputs

class Moktashif_CLI:
    def __init__(self):
        self.parser = self._create_parser()

    def _create_parser(self) -> argparse.ArgumentParser:
        parser = argparse.ArgumentParser(
            "Moktashif_AI",
            description="AI-Powered Penetration Testing Framework"
        )

        parser.add_argument(
            "--url",
            type=str,
            required=True,
            help="Web Application URL Or IP (e.g., http://127.0.0.1/DVWA/)"
        )
        
        parser.add_argument(
            "--check-deps",
            action="store_true",
            help="Check if all required dependencies are installed"
        )
        
        parser.add_argument(
            "--install-deps",
            action="store_true",
            help="Install missing dependencies (requires sudo)"
        )
        
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Enable verbose output"
        )

        return parser

    def parse_args(self):
        args = self.parser.parse_args()
        return args

def check_dependencies():
    """Check if required tools are installed"""
    required_tools = [
        'curl', 'jq', 'nc', 'nmap', 'sqlmap', 'dirb', 
        'gobuster', 'hydra', 'nikto', 'python3'
    ]
    
    missing_tools = []
    available_tools = []
    
    for tool in required_tools:
        try:
            result = subprocess.run(
                ['which', tool], 
                check=True, 
                capture_output=True, 
                text=True
            )
            available_tools.append(tool)
        except subprocess.CalledProcessError:
            missing_tools.append(tool)
    
    return available_tools, missing_tools

def install_dependencies():
    """Install missing dependencies using the installation script"""
    script_path = os.path.join(os.path.dirname(__file__), 'install_dependencies.sh')
    
    if not os.path.exists(script_path):
        print("Error: install_dependencies.sh not found")
        print("Please ensure the installation script is in the same directory as main.py")
        return False
    
    try:
        # Make script executable
        os.chmod(script_path, 0o755)
        
        # Run installation script
        result = subprocess.run(['sudo', script_path], check=True)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        return False
    except FileNotFoundError:
        print("Error: sudo not found. Please run the installation script manually with admin privileges.")
        return False

def validate_url(url):
    """Validate the provided URL"""
    try:
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            return False, "Invalid URL format. Please include protocol (http:// or https://)"
        
        if parsed.scheme not in ['http', 'https']:
            return False, "Only HTTP and HTTPS protocols are supported"
        
        return True, "URL is valid"
    except Exception as e:
        return False, f"URL validation error: {str(e)}"

def parse_domain(link):
    """Strips a URL down to its scheme and network location"""
    parsed_url = urlparse(link)
    domain_name = f"{parsed_url.scheme}://{parsed_url.netloc}"
    return domain_name

def parse_pathname(link):
    """Extracts the last segment of the path"""
    parsed_url = urlparse(link)
    path_name = parsed_url.path.rstrip('/').split('/')[-1]
    return path_name if path_name else "Home"

def create_output_directory():
    """Create output directory for reports"""
    output_dir = "moktashif_reports"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    return output_dir

def save_results(output_dir, url, final_data, final_results):
    """Save all results to files"""
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    domain = parse_domain(url).replace("://", "_").replace("/", "_")
    
    # Save analysis data
    analysis_file = os.path.join(output_dir, f"analysis_{domain}_{timestamp}.json")
    with open(analysis_file, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, indent=2, ensure_ascii=False)
    
    # Save exploit results
    results_file = os.path.join(output_dir, f"results_{domain}_{timestamp}.txt")
    with open(results_file, 'w', encoding='utf-8') as f:
        f.write(f"Moktashif_AI Penetration Testing Results\n")
        f.write(f"Target: {url}\n")
        f.write(f"Timestamp: {timestamp}\n")
        f.write("=" * 50 + "\n\n")
        
        for i, result in enumerate(final_results, 1):
            f.write(f"Test {i}:\n")
            f.write(result)
            f.write("\n" + "=" * 30 + "\n\n")
    
    return analysis_file, results_file

# GPT Agent Initialization
try:
    Discovery_Agent = Agents.DiscoveryAgent(prompts.Prompts.init_discovery)
    Planner_Agent = Agents.PlannerAgent(prompts.Prompts.init_planner)
    Exploit_Agent = Agents.ExploitAgent(prompts.Prompts.init_exploit)
except Exception as e:
    print(f"Error initializing AI agents: {e}")
    print("Please check your OpenAI API key and network connection")
    sys.exit(1)

def discover_and_test_page(url, page_name="Home"):
    """Discover and test a single page"""
    l = Logger()
    
    try:
        l.Log(f"Analyzing page: {page_name} - {url}")
        
        # Web Analysis
        analyzer = WebAnalyzer.WebAnalyzer(url)
        result, extend_info = analyzer.analyze_page()
        Final_Data.append([page_name, result, extend_info])
        
        l.Log(f"Sending {page_name} analysis to AI Discovery Agent...")
        
        # Discovery Phase
        discovery_prompt = (
            f"Name: {page_name}\n"
            f"Basic Result: {result}\n"
            f"Detailed Analysis With PageSource: {extend_info}\n\n"
        )
        
        discovery_output = Discovery_Agent.discover_website(discovery_prompt)
        l.Log(f"Discovery phase completed for {page_name}")
        
        # Planning Phase
        planner_prompt = (
            f"Detailed Json Analysis: {discovery_output}\n"
            f"Page Source Context: {extend_info}\n\n"
        )
        
        planner_output = Planner_Agent.plan_decision_tree_for_website(planner_prompt)
        l.Log(f"Planning phase completed for {page_name}")
        
        # Exploitation Phase
        exploit_prompt = f"""
Given this decision tree, evaluate it systematically and determine if the application is vulnerable.

DECISION TREE:
{planner_output}

DISCOVERY CONTEXT:
{discovery_output}

EXECUTION INSTRUCTIONS:
1. Follow the decision tree step by step
2. Execute commands one at a time
3. Evaluate success/failure for each task
4. Move to next task based on decision tree logic
5. Handle missing tools gracefully
6. Generate final report when complete

OUTPUT FORMAT REQUIRED:
- Vulnerability:
  - Vulnerability Category: [category]
  - Affected Parameters: [parameters]
  - Entry Point: [url]

- Proof of Concept:
  - Payload: [payload]
  - Reproduction Steps:
    1. [step 1]
    2. [step 2]
    3. [step 3]

- Prerequisites:
  - [prerequisite list]

- Success Conditions:
  - [success conditions]

- Exploitation Path:
  - Step: [step description]
  - Command: [command used]
  - Outcome: [result]
  - Notes: [notes]

IMPORTANT: 
- Use --batch flag for non-interactive tools
- Handle missing tools by using alternatives
- Stop execution when vulnerability found or decision tree complete
- Report "No vulnerabilities found" if testing completes without findings
"""

        exploit_output = Exploit_Agent.exploit_agent_for_website(exploit_prompt)
        Final_Result.append(exploit_output)
        l.Log(f"Exploitation phase completed for {page_name}")
        
        return True
        
    except Exception as e:
        l.Log(f"Error analyzing {page_name}: {str(e)}", "Error")
        return False

def discover_additional_pages(base_url):
    """Discover and test additional pages from the home page links"""
    if not Final_Data:
        return
    
    l = Logger()
    home_data = Final_Data[0]  # Home page data
    extend_info = home_data[2]
    
    additional_urls = []
    base_domain = parse_domain(base_url)
    
    # Extract internal links
    for link_data in extend_info.get('links', []):
        url_inside = link_data.get('url', '')
        
        # Only process internal links that are PHP files or same domain
        if (url_inside.startswith(base_domain) and 
            url_inside != base_url and
            url_inside not in additional_urls):
            additional_urls.append(url_inside)
    
    l.Log(f"Found {len(additional_urls)} additional pages to test")
    
    # Test additional pages
    for url in additional_urls[:5]:  # Limit to 5 additional pages
        page_name = parse_pathname(url).capitalize()
        discover_and_test_page(url, page_name)

def main():
    l = Logger()
    
    try:
        # Parse CLI arguments
        cli = Moktashif_CLI()
        args = cli.parse_args()
        
        # Check dependencies if requested
        if args.check_deps:
            l.Log("Checking dependencies...")
            available, missing = check_dependencies()
            
            print(f"Available tools: {', '.join(available)}")
            if missing:
                print(f"Missing tools: {', '.join(missing)}")
                print("Run with --install-deps to install missing tools")
                sys.exit(1)
            else:
                print("All required tools are available!")
                sys.exit(0)
        
        # Install dependencies if requested
        if args.install_deps:
            l.Log("Installing dependencies...")
            if install_dependencies():
                l.Log("Dependencies installed successfully")
            else:
                l.Log("Failed to install dependencies", "Error")
                sys.exit(1)
            return
        
        # Validate URL
        url = args.url
        is_valid, message = validate_url(url)
        if not is_valid:
            l.Log(f"URL validation failed: {message}", "Error")
            sys.exit(1)
        
        # Check dependencies before starting
        available, missing = check_dependencies()
        if missing:
            l.Log(f"Missing required tools: {', '.join(missing)}", "Error")
            l.Log("Run with --install-deps to install them", "Info")
            sys.exit(1)
        
        l.Log(f"Starting Moktashif_AI analysis for: {url}")
        
        # Create output directory
        output_dir = create_output_directory()
        
        # Test home page
        if not discover_and_test_page(url, "Home"):
            l.Log("Failed to analyze home page", "Error")
            sys.exit(1)
        
        # Test additional pages
        discover_additional_pages(url)
        
        # Save results
        analysis_file, results_file = save_results(output_dir, url, Final_Data, Final_Result)
        
        l.Log("Analysis completed successfully!")
        l.Log(f"Analysis data saved to: {analysis_file}")
        l.Log(f"Results saved to: {results_file}")
        
        # Print summary
        print("\n" + "="*50)
        print("MOKTASHIF_AI ANALYSIS SUMMARY")
        print("="*50)
        print(f"Target: {url}")
        print(f"Pages analyzed: {len(Final_Data)}")
        print(f"Tests performed: {len(Final_Result)}")
        print(f"Results saved to: {output_dir}")
        print("="*50)
        
    except KeyboardInterrupt:
        l.Log("Analysis interrupted by user", "Error")
        sys.exit(1)
    except Exception as e:
        l.Log(f"Critical error during analysis: {str(e)}", "Error")
        sys.exit(1)

if __name__ == "__main__":
    main()
