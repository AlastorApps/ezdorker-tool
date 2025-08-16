import argparse
import time
import webbrowser
import re
import random
import json
from urllib.parse import quote
import requests
from bs4 import BeautifulSoup
from colorama import init, Fore, Style
from tqdm import tqdm
import logging

# Inizializza colorama per i colori cross-platform
init()

# Configurazione logging
logging.basicConfig(
    level=logging.INFO,
    format=f'{Fore.CYAN}%(asctime)s{Style.RESET_ALL} - {Fore.GREEN}%(levelname)s{Style.RESET_ALL}: %(message)s',
    handlers=[
        logging.FileHandler('ezdorker.log'),
        logging.StreamHandler()
    ]
)

# Configurazione
CONFIG = {
    "delay": 2,          # Ritardo tra le richieste (evita blocchi)
    "max_results": 50,   # Limite risultati per ricerca
    "timeout": 30,       # Timeout per le richieste HTTP
    "retries": 3,        # Tentativi di ripetizione in caso di errore
    "max_workers": 5     # Per eventuale multithreading
}

# User Agents aggiornati (evitano il blocco)
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
]

# Dorks organizzati per categoria
DORKS = {
    "filetype": [
        "site:{target} filetype:pdf",
        "site:{target} filetype:doc",
        "site:{target} filetype:xls",
        "site:{target} filetype:txt",
        "site:{target} filetype:conf"
    ],
    "login": [
        "site:{target} inurl:login",
        "site:{target} intitle:login",
        "site:{target} inurl:admin",
        "site:{target} intext:'login page'"
    ],
    "config": [
        "site:{target} ext:xml | ext:conf | ext:cnf | ext:reg | ext:inf | ext:rdp | ext:cfg | ext:txt | ext:ora | ext:ini",
        "site:{target} intext:'password' filetype:txt",
        "site:{target} intext:'username' filetype:txt"
    ],
    "vulnerabilities": [
        "site:{target} inurl:'wp-content'",
        "site:{target} intext:'index of /'",
        "site:{target} intext:'sql syntax near'",
        "site:{target} intext:'warning: mysql'"
    ],
    "subdomains": [
        "site:*.{target} -www",
        "site:*.{target} -shop",
        "site:*.{target} -blog"
    ]
}

# Motori di ricerca supportati (BUGFIX APPLICATO)
SEARCH_ENGINES = {
    "google": {
        "url": "https://www.google.com/search?q={query}&num={num}",
        "parser": "google",
        "params": {"num": 50}
    },
    "bing": {
        "url": "https://www.bing.com/search?q={query}&count={count}",
        "parser": "bing",
        "params": {"count": 50}
    },
    "duckduckgo": {
        "url": "https://html.duckduckgo.com/html/?q={query}",
        "parser": "duckduckgo"
    },
    "yahoo": {
        "url": "https://search.yahoo.com/search?p={query}&n={n}",
        "parser": "yahoo",
        "params": {"n": 50}
    },
    "baidu": {
        "url": "https://www.baidu.com/s?wd={query}&rn={rn}",
        "parser": "baidu",
        "params": {"rn": 50}
    },
    "yandex": {
        "url": "https://yandex.com/search/?text={query}&numdoc={numdoc}",
        "parser": "yandex",
        "params": {"numdoc": 50}
    }
}

class EZDorker:
    def __init__(self, proxy=None):
        """Inizializza EZDorker con proxy opzionale."""
        self.total_requests = 0
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': self.get_random_user_agent()})
        
        if proxy:
            self.set_proxy(proxy)
        
        logging.info("EZDorker inizializzato ✅")

    def set_proxy(self, proxy):
        """Configura un proxy per tutte le richieste."""
        if not re.match(r'^(http|https|socks5)://[\w.-]+(:\d+)?$', proxy):
            raise ValueError("Formato proxy non valido. Esempio: http://proxy.example.com:8080")
        
        self.session.proxies = {"http": proxy, "https": proxy}
        logging.info(f"Proxy configurato: {proxy}")

    def get_random_user_agent(self):
        """Restituisce un User-Agent casuale."""
        return random.choice(USER_AGENTS)

    def search(self, dork, engine="google", delay=CONFIG["delay"]):
        """Esegue una ricerca sul motore specificato."""
        if engine not in SEARCH_ENGINES:
            raise ValueError(f"Motore non supportato: {engine}")
        
        engine_config = SEARCH_ENGINES[engine]
        url = engine_config["url"].format(
            query=quote(dork),
            **engine_config.get("params", {})
        )
        
        for attempt in range(CONFIG["retries"]):
            try:
                time.sleep(delay)
                self.total_requests += 1
                self.session.headers.update({'User-Agent': self.get_random_user_agent()})
                
                response = self.session.get(url, timeout=CONFIG["timeout"])
                response.raise_for_status()
                
                return self.parse_results(response.text, engine_config["parser"], dork, engine)
            
            except requests.exceptions.RequestException as e:
                if attempt == CONFIG["retries"] - 1:
                    logging.error(f"Errore ricerca {engine.upper()} (tentativo {attempt + 1}/{CONFIG['retries']}): {e}")
                    return []
                time.sleep(2 * (attempt + 1))  # Backoff esponenziale

    def parse_results(self, html, parser_type, dork, engine):
        """Analizza i risultati HTML."""
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        
        try:
            if parser_type == "google":
                for g in soup.find_all('div', class_='g'):
                    anchor = g.find('a')
                    if anchor and anchor.get('href'):
                        results.append({
                            'title': anchor.text if anchor.text else 'N/A',
                            'link': anchor['href'],
                            'description': g.find('div', class_='VwiC3b').text if g.find('div', class_='VwiC3b') else 'N/A',
                            'dork': dork,
                            'engine': engine
                        })
            
            elif parser_type == "bing":
                for li in soup.find_all('li', class_='b_algo'):
                    anchor = li.find('a')
                    if anchor:
                        results.append({
                            'title': anchor.text if anchor.text else 'N/A',
                            'link': anchor.get('href'),
                            'description': li.find('p').text if li.find('p') else 'N/A',
                            'dork': dork,
                            'engine': engine
                        })
            
            elif parser_type == "duckduckgo":
                for result in soup.find_all('div', class_='result'):
                    anchor = result.find('a', class_='result__a')
                    if anchor:
                        results.append({
                            'title': anchor.text,
                            'link': anchor.get('href'),
                            'description': result.find('a', class_='result__snippet').text if result.find('a', class_='result__snippet') else 'N/A',
                            'dork': dork,
                            'engine': engine
                        })
            
            elif parser_type == "yahoo":
                for div in soup.find_all('div', class_='algo'):
                    anchor = div.find('a')
                    if anchor:
                        results.append({
                            'title': anchor.text if anchor.text else 'N/A',
                            'link': anchor.get('href'),
                            'description': div.find('p', class_='fz-ms').text if div.find('p', class_='fz-ms') else 'N/A',
                            'dork': dork,
                            'engine': engine
                        })
            
            elif parser_type == "baidu":
                for result in soup.find_all('div', class_='result'):
                    anchor = result.find('a')
                    if anchor:
                        results.append({
                            'title': anchor.text,
                            'link': anchor.get('href'),
                            'description': result.find('div', class_='c-abstract').text if result.find('div', class_='c-abstract') else 'N/A',
                            'dork': dork,
                            'engine': engine
                        })
            
            elif parser_type == "yandex":
                for item in soup.find_all('li', class_='serp-item'):
                    anchor = item.find('a', class_='organic__url')
                    if anchor:
                        results.append({
                            'title': anchor.text,
                            'link': anchor.get('href'),
                            'description': item.find('div', class_='organic__content-wrapper').text if item.find('div', class_='organic__content-wrapper') else 'N/A',
                            'dork': dork,
                            'engine': engine
                        })
        
        except Exception as e:
            logging.error(f"Errore parsing {engine.upper()}: {e}")
        
        return results[:CONFIG["max_results"]]

    def passive_recon(self, target, output_file=None, open_browser=False, engines=["google"], categories=None, verbose=False):
        """Esegue la ricognizione passiva."""
        try:
            logging.info(f"\n{Fore.GREEN}[+] EZDorker - Passive Reconnaissance Tool{Style.RESET_ALL}")
            logging.info(f"{Fore.CYAN}[+] Target:{Style.RESET_ALL} {target}")
            
            dorks = self.generate_dorks(target, categories)
            logging.info(f"{Fore.CYAN}[+] Generati {len(dorks)} dorks{Style.RESET_ALL}")
            
            results = []
            start_time = time.time()
            
            for dork in tqdm(dorks, desc="Elaborazione dorks", disable=not verbose):
                if verbose:
                    logging.info(f"\n{Fore.YELLOW}[+] Eseguendo dork:{Style.RESET_ALL} {dork}")
                
                for engine in engines:
                    try:
                        engine_results = self.search(dork, engine)
                        results.extend(engine_results)
                        
                        if verbose:
                            logging.info(f"  {Fore.GREEN}[+] {engine.upper()}:{Style.RESET_ALL} trovati {len(engine_results)} risultati")
                        
                        if open_browser and engine_results:
                            webbrowser.open_new_tab(SEARCH_ENGINES[engine]["url"].format(query=quote(dork), **SEARCH_ENGINES[engine].get("params", {})))
                    
                    except Exception as e:
                        logging.error(f"  {Fore.RED}[-] Errore con {engine.upper()}:{Style.RESET_ALL} {str(e)}")
            
            if output_file:
                self.save_results(results, output_file)
                logging.info(f"\n{Fore.GREEN}[+] Risultati salvati in:{Style.RESET_ALL} {output_file}")
            
            elapsed_time = time.time() - start_time
            logging.info(f"\n{Fore.GREEN}[+] Ricognizione completata!{Style.RESET_ALL}")
            logging.info(f"{Fore.CYAN}[+] Tempo totale:{Style.RESET_ALL} {elapsed_time:.2f} secondi")
            logging.info(f"{Fore.CYAN}[+] Risultati totali:{Style.RESET_ALL} {len(results)}")
            
            return results
        
        except KeyboardInterrupt:
            logging.info(f"\n{Fore.YELLOW}[!] Interrotto dall'utente{Style.RESET_ALL}")
        except Exception as e:
            logging.error(f"\n{Fore.RED}[!] Errore critico: {e}{Style.RESET_ALL}")

    def save_results(self, results, output_file):
        """Salva i risultati in JSON, CSV o TXT."""
        try:
            if output_file.endswith('.json'):
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(results, f, indent=2, ensure_ascii=False)
            elif output_file.endswith('.csv'):
                import csv
                with open(output_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=results[0].keys())
                    writer.writeheader()
                    writer.writerows(results)
            else:  # TXT
                with open(output_file, 'w', encoding='utf-8') as f:
                    for result in results:
                        f.write(f"Dork: {result['dork']}\n")
                        f.write(f"Engine: {result['engine']}\n")
                        f.write(f"Title: {result['title']}\n")
                        f.write(f"Link: {Fore.LIGHTYELLOW_EX}{result['link']}{Style.RESET_ALL}\n")
                        f.write(f"Description: {result['description'][:200]}...\n\n")
        except Exception as e:
            logging.error(f"{Fore.RED}Errore salvataggio risultati: {e}{Style.RESET_ALL}")

def main():
    parser = argparse.ArgumentParser(description="EZDorker - Advanced Search Engine Dorking Tool")
    parser.add_argument("target", help="Dominio target (esempio: example.com)")
    parser.add_argument("-o", "--output", help="File di output (es: risultati.json)")
    parser.add_argument("-e", "--engines", nargs='+', choices=SEARCH_ENGINES.keys(), default=["google"], help="Motori di ricerca")
    parser.add_argument("-c", "--categories", nargs='+', choices=DORKS.keys(), default=None, help="Categorie di dork")
    parser.add_argument("-b", "--browser", action="store_true", help="Apri i dorks nel browser")
    parser.add_argument("-v", "--verbose", action="store_true", help="Output dettagliato")
    parser.add_argument("-p", "--proxy", help="Proxy server (es: http://proxy.example.com:8080)")
    
    args = parser.parse_args()
    
    try:
        dorker = EZDorker(proxy=args.proxy)
        dorker.passive_recon(
            target=args.target,
            output_file=args.output,
            open_browser=args.browser,
            engines=args.engines,
            categories=args.categories,
            verbose=args.verbose
        )
    except Exception as e:
        logging.error(f"{Fore.RED}Errore durante l'esecuzione: {e}{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
