import argparse
import time
import webbrowser
from urllib.parse import quote
import requests
from bs4 import BeautifulSoup
import random
import json
from datetime import datetime

# Configurazione
CONFIG = {
    "delay": 2,
    "max_results": 50,
    "timeout": 10
}

# User agents per evitare il blocco
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"
]

# Dorks comuni organizzati per categoria
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

# Motori di ricerca supportati
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
        "url": "https://search.yahoo.com/search?p={query}&n={num}",
        "parser": "yahoo",
        "params": {"n": 50}
    },
    "baidu": {
        "url": "https://www.baidu.com/s?wd={query}&rn={num}",
        "parser": "baidu",
        "params": {"rn": 50}
    },
    "yandex": {
        "url": "https://yandex.com/search/?text={query}&numdoc={num}",
        "parser": "yandex",
        "params": {"numdoc": 50}
    }
}

class EZDorker:
    def __init__(self):
        self.total_requests = 0
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': self.get_random_user_agent()})
    
    def get_random_user_agent(self):
        return random.choice(USER_AGENTS)
    
    def search(self, dork, engine="google", delay=CONFIG["delay"]):
        """Esegue una ricerca sul motore specificato"""
        if engine not in SEARCH_ENGINES:
            raise ValueError(f"Motore di ricerca non supportato: {engine}")
        
        engine_config = SEARCH_ENGINES[engine]
        url = engine_config["url"].format(
            query=quote(dork),
            **engine_config.get("params", {})
        )
        
        try:
            time.sleep(delay)
            self.total_requests += 1
            self.session.headers.update({'User-Agent': self.get_random_user_agent()})
            
            response = self.session.get(
                url,
                timeout=CONFIG["timeout"]
            )
            response.raise_for_status()
            
            return self.parse_results(response.text, engine_config["parser"], dork, engine)
        except Exception as e:
            print(f"Errore durante la ricerca {engine.upper()}: {e}")
            return []
    
    def parse_results(self, html, parser_type, dork, engine):
        """Analizza i risultati HTML in base al motore di ricerca"""
        soup = BeautifulSoup(html, 'html.parser')
        results = []
        
        if parser_type == "google":
            for g in soup.find_all('div', class_='g'):
                anchor = g.find('a')
                if anchor and anchor.get('href'):
                    link = anchor['href']
                    title = g.find('h3')
                    desc = g.find('div', class_='VwiC3b')
                    results.append({
                        'title': title.text if title else 'N/A',
                        'link': link,
                        'description': desc.text if desc else 'N/A',
                        'dork': dork,
                        'engine': engine
                    })
        
        elif parser_type == "bing":
            for li in soup.find_all('li', class_='b_algo'):
                anchor = li.find('a')
                if anchor:
                    link = anchor.get('href')
                    title = li.find('h2')
                    desc = li.find('p')
                    results.append({
                        'title': title.text if title else 'N/A',
                        'link': link,
                        'description': desc.text if desc else 'N/A',
                        'dork': dork,
                        'engine': engine
                    })
        
        elif parser_type == "duckduckgo":
            for result in soup.find_all('div', class_='result'):
                anchor = result.find('a', class_='result__a')
                if anchor:
                    link = anchor.get('href')
                    title = anchor.text
                    desc = result.find('a', class_='result__snippet')
                    results.append({
                        'title': title,
                        'link': link,
                        'description': desc.text if desc else 'N/A',
                        'dork': dork,
                        'engine': engine
                    })
        
        # Aggiungi altri parser per i motori rimanenti
        
        return results[:CONFIG["max_results"]]
    
    def open_in_browser(self, dork, engine="google"):
        """Apre il dork nel browser predefinito"""
        if engine not in SEARCH_ENGINES:
            print(f"Motore di ricerca non supportato: {engine}")
            return
        
        url = SEARCH_ENGINES[engine]["url"].format(
            query=quote(dork),
            **SEARCH_ENGINES[engine].get("params", {})
        )
        webbrowser.open_new_tab(url)
    
    def generate_dorks(self, target, categories=None):
        """Genera dorks per il target specificato"""
        if categories is None:
            categories = DORKS.keys()
        
        generated_dorks = []
        for category in categories:
            if category in DORKS:
                for dork_template in DORKS[category]:
                    generated_dorks.append(dork_template.format(target=target))
        
        return generated_dorks
    
    def passive_recon(self, target, output_file=None, open_browser=False, 
                    engines=["google"], categories=None, verbose=False):
        """Esegue la ricognizione passiva"""
        print(f"\n[+] EZDorker - Passive Reconnaissance Tool")
        print(f"[+] Target: {target}")
        print(f"[+] Motori di ricerca: {', '.join(engines)}")
        print(f"[+] Categorie dork: {', '.join(categories) if categories else 'all'}")
        
        dorks = self.generate_dorks(target, categories)
        print(f"[+] Generati {len(dorks)} dorks")
        
        results = []
        start_time = time.time()
        
        for i, dork in enumerate(dorks, 1):
            if verbose:
                print(f"\n[{i}/{len(dorks)}] Eseguendo dork: {dork}")
            
            for engine in engines:
                try:
                    engine_results = self.search(dork, engine)
                    results.extend(engine_results)
                    
                    if verbose:
                        print(f"  [+] {engine.upper()}: trovati {len(engine_results)} risultati")
                    
                    if open_browser and engine_results:
                        self.open_in_browser(dork, engine)
                
                except Exception as e:
                    print(f"  [-] Errore con {engine.upper()}: {str(e)}")
                    continue
        
        # Salva i risultati
        if output_file:
            self.save_results(results, output_file)
            print(f"\n[+] Risultati salvati in: {output_file}")
        
        elapsed_time = time.time() - start_time
        print(f"\n[+] Ricognizione completata!")
        print(f"[+] Tempo totale: {elapsed_time:.2f} secondi")
        print(f"[+] Richieste totali: {self.total_requests}")
        print(f"[+] Risultati totali: {len(results)}")
        
        return results
    
    def save_results(self, results, output_file):
        """Salva i risultati in vari formati in base all'estensione del file"""
        if output_file.endswith('.json'):
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2)
        elif output_file.endswith('.csv'):
            import csv
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=results[0].keys())
                writer.writeheader()
                writer.writerows(results)
        else:  # Formato testo semplice di default
            with open(output_file, 'w', encoding='utf-8') as f:
                for result in results:
                    f.write(f"Dork: {result['dork']}\n")
                    f.write(f"Engine: {result['engine']}\n")
                    f.write(f"Title: {result['title']}\n")
                    f.write(f"Link: {result['link']}\n")
                    f.write(f"Description: {result['description'][:200]}...\n\n")

def main():
    parser = argparse.ArgumentParser(
        description="EZDorker - Advanced Search Engine Dorking Tool",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("target", help="Dominio target (esempio: example.com)")
    parser.add_argument("-o", "--output", help="File di output per i risultati")
    parser.add_argument("-e", "--engines", nargs='+', 
                      choices=SEARCH_ENGINES.keys(), default=["google"],
                      help="Motori di ricerca da utilizzare")
    parser.add_argument("-c", "--categories", nargs='+', 
                      choices=DORKS.keys(), default=None,
                      help="Categorie di dork da generare")
    parser.add_argument("-b", "--browser", action="store_true",
                      help="Apri i dorks nel browser")
    parser.add_argument("-v", "--verbose", action="store_true",
                      help="Mostra output dettagliato")
    
    args = parser.parse_args()
    
    dorker = EZDorker()
    dorker.passive_recon(
        target=args.target,
        output_file=args.output,
        open_browser=args.browser,
        engines=args.engines,
        categories=args.categories,
        verbose=args.verbose
    )

if __name__ == "__main__":
    main()
