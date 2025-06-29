# AI-based-Scan-Engine

## Table of Contents

1. [Overview](#overview)
2. [Key Features](#key-features)
3. [Architecture](#architecture)
4. [Prerequisites](#prerequisites)
5. [Installation](#installation)
6. [Usage](#usage)
7. [How It Works](#how-it-works)
8. [Output](#output)
9. [Supported Tools](#supported-tools)
10. [Troubleshooting](#troubleshooting)
11. [Security Considerations](#security-considerations)
12. [Contributing](#contributing)
13. [License](#license)
14. [Author](#author)
15. [Disclaimer](#disclaimer)
16. [Acknowledgments](#acknowledgments)

## Overview

AI-based-Scan-Engine, also known as Moktashif_AI, is an advanced AI-powered penetration testing framework that leverages artificial intelligence to automate and enhance web application security assessments. The framework combines traditional penetration testing tools with OpenAI's language models to provide intelligent vulnerability discovery, planning, and exploitation capabilities.

## Key Features

- **AI-Driven Security Analysis**: Three specialized AI agents work together to discover vulnerabilities, plan testing strategies, and execute exploits
- **Automated Web Analysis**: Comprehensive scanning of web applications including forms, inputs, links, cookies, and security headers
- **Intelligent Decision Trees**: Dynamic generation of penetration testing workflows based on discovered attack surfaces
- **Native Tool Integration**: Seamless integration with standard Kali Linux penetration testing tools
- **Detailed Reporting**: Comprehensive vulnerability reports with proof-of-concept demonstrations and reproduction steps
- **Multi-Page Analysis**: Automatic discovery and testing of linked pages within the target application

## Architecture

The framework consists of four main components:

- **Web Analyzer**: Uses Playwright for comprehensive web application analysis
- **AI Agents**: Three specialized agents (Discovery, Planner, Exploit) powered by OpenAI GPT models
- **Utils Module**: Handles logging, agent orchestration, and tool execution
- **Prompts Module**: Contains carefully crafted system prompts for AI agent behavior

## Prerequisites

- Python 3.8 or higher
- Kali Linux or similar penetration testing distribution
- OpenAI API key (via OpenRouter)
- Administrative privileges for system dependency installation
- Active internet connection

## Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/AI-based-Scan-Engine.git
cd AI-based-Scan-Engine
```

### Step 2: Install System Dependencies

```bash
sudo chmod +x dependency_installer.sh
sudo ./dependency_installer.sh
```

### Step 3: Install Python Dependencies

Option A - Using Virtual Environment (Recommended):

```bash
python3 -m venv moktashif_venv
source moktashif_venv/bin/activate
pip install -r requirements.txt
```

Option B - Using the Python Installer:

```bash
python3 python_dep_installer.py
```

### Step 4: Configure API Key

Create a `.env` file in the project root:

```bash
echo "OPENAI_API_KEY=your_openrouter_api_key_here" > .env
```

## Usage

### Basic Usage

```bash
python main.py --url http://target-website.com
```

### Verify Dependencies

```bash
python main.py --check-deps
```

### Install Missing Dependencies

```bash
python main.py --install-deps
```

### Verbose Mode

```bash
python main.py --url http://target-website.com --verbose
```

## How It Works
[![image](https://github.com/user-attachments/assets/c6c098f9-ff5f-4d56-9de7-831292398872)
](https://app-cdn.readytensor.ai/publications/resources/hubId=4496/publicationId=1677/image.png?Expires=1751230124&Key-Pair-Id=K2V2TN6YBJQHTG&Signature=sLX71SVHsEOIXkyFnxAtKvRfKsAiEcokFHg~5NHhhMa5ozAm-Gmk-RGQavAeJe8pOm0o4vQ3vqXZiSgkNrGudQx7dUEbe-t0c4MG1bRIxTof7B0oC1FUFAhqTjsbiX-5DrxD1cMILUduybnMbnR-kOeequcHQ7rLJlJVBCYLSXPfubG0883tWQV5Sd1ffLuBn-8hpbn7GQwUxbcLK06tav6Afdaz7m6c7h80J6wZPs8F8~8RtnmXZsWPc0lpCwm1QvfDdbRvrj3huy74QCHDQ-8hyW~O6G5KE~vnZEHfFAkxPWZOBHFFjqLQw41C-~XNaX9Hhh5jArsSLrd0ujUyvQ__)
### Phase 1: Discovery

The Web Analyzer performs a comprehensive analysis of the target application:
- Extracts page structure, forms, and input fields
- Identifies authentication mechanisms
- Collects cookies and security headers
- Maps internal and external links

### Phase 2: Planning

The Planner Agent generates a decision tree for testing:
- Creates specific test cases based on discovered vulnerabilities
- Defines success/failure criteria for each test
- Provides alternative approaches for tool failures
- Prioritizes tests based on severity and likelihood

### Phase 3: Exploitation

The Exploit Agent executes the testing plan:
- Runs penetration testing commands systematically
- Evaluates results against predefined criteria
- Handles tool failures with alternative approaches
- Generates detailed vulnerability reports

## Output

All results are saved in the `moktashif_reports` directory:

- **Analysis Data** (`analysis_[domain]_[timestamp].json`): Complete page analysis and vulnerability data
- **Test Results** (`results_[domain]_[timestamp].txt`): Detailed penetration testing results
- **Page Sources** (`page_source_[page]_[timestamp].html`): Archived HTML content
- **Extracted Data** (`extracted_links_[page]_[timestamp].txt`, `cookies_[page]_[timestamp].txt`): Parsed information

## Supported Tools

### Network Analysis
- curl, wget, netcat, nmap, tcpdump

### Content Discovery
- ffuf, wfuzz, dirb, gobuster

### Authentication Testing
- hydra, medusa, john

### Exploitation
- sqlmap, xsser, commix

### Additional Utilities
- jq, python, base64, grep

## Troubleshooting

### Common Issues

1. **Missing Dependencies**
   ```bash
   python main.py --check-deps
   python main.py --install-deps
   ```

2. **API Key Errors**
   - Verify `.env` file exists with a valid API key
   - Check OpenRouter account credits

3. **Permission Errors**
   ```bash
   sudo ./dependency_installer.sh
   ```

4. **Network Timeouts**
   - Verify target URL accessibility
   - Check internet connection

## Security Considerations

- **Authorization Required**: Only test systems you own or have explicit permission to test
- **Rate Limiting**: The framework implements delays to avoid overwhelming targets
- **Non-Destructive**: Tests are designed to identify vulnerabilities without causing damage
- **Legal Compliance**: Users must comply with all applicable laws and regulations

## Contributing

We welcome contributions! Please:

1. Fork the repository
2. Create a feature branch
3. Follow existing code style
4. Add appropriate error handling
5. Update documentation
6. Submit a pull request

For major changes, please open an issue first to discuss the proposed changes.

## License

This project is licensed under the MIT License. See the LICENSE file for full terms.

## Author

**Mohamed Taha Khattab**  
Email: mohamed.taha.khattab0@gmail.com

## Disclaimer

**IMPORTANT**: This tool is for educational and authorized security testing purposes only.

By using this framework, you acknowledge that:
- You have proper authorization for all systems you test
- You will not use this tool for illegal or unethical purposes
- You understand the risks associated with penetration testing
- You accept full responsibility for your actions

The author and contributors assume no liability for misuse or damage caused by this program. The framework is provided "as is" without warranty of any kind.

## Acknowledgments

Special thanks to:

- **WalTeR-RE** (https://github.com/WalTeR-RE) - For invaluable contributions to security research and inspiration in developing AI-enhanced security tools

- **Yosif Qasim** (https://github.com/yosif-qasim) - For expertise in web application security and modern penetration testing methodologies

Additional recognition goes to:
- The OpenAI team for powerful language models
- Playwright developers for excellent web automation
- Maintainers of all integrated security tools
- The open-source security community

---

*This project stands on the shoulders of giants in the security research field.*
