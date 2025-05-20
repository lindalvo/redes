import socket
import time
from datetime import datetime

QUANTIDADE = 10
TAMANHO_PACOTE = 64  # bytes
TIMEOUT = 1  # segundos
PORTA_SERVIDOR = 12000

def do_udp_ping(destino, quantidade, tamanho_pacote):
    try:
        dest_ip = socket.gethostbyname(destino)
    except socket.gaierror:
        print(f"Erro: não foi possível resolver {destino}")
        return

    print(f"\nIniciando UDP Ping para {destino} ({dest_ip}) com {quantidade} pacotes de {tamanho_pacote} bytes:\n")

    rtts = []

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(TIMEOUT)
        for i in range(1, quantidade + 1):
            data_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            #mensagem_base = f"PING {i} em {data_hora}"
            mensagem_base =  "UFPA Mestrado em Ciência da Computação"
            padding = "X" * max(0, TAMANHO_PACOTE - len(mensagem_base))
            mensagem = (mensagem_base + padding).encode()

            start = time.time()
            try:
                sock.sendto(mensagem, (dest_ip, PORTA_SERVIDOR))
                resposta, servidor = sock.recvfrom(1024)
                rtt = (time.time() - start) * 1000
                rtts.append(rtt)
                resposta_texto = resposta.decode()
                #print(f"Resposta {i}: {len(resposta)} bytes, RTT = {rtt:.2f} ms")
                print(f"Resposta {i+1} de {servidor[0]}: '{resposta_texto}' | RTT = {rtt:.2f} ms")
            except socket.timeout:
                print(f"Resposta {i}: Timeout")
            time.sleep(1)

    print("\n--- Estatísticas ---")
    enviados = quantidade
    recebidos = len(rtts)
    perdidos = enviados - recebidos
    perda_pct = (perdidos / enviados) * 100

    print(f"{enviados} enviados, {recebidos} recebidos, {perda_pct:.0f}% perdidos")

    if rtts:
        print(f"RTT mínimo = {min(rtts):.2f} ms, máximo = {max(rtts):.2f} ms, média = {sum(rtts)/len(rtts):.2f} ms")

def main():
    destino = input("Digite o IP ou hostname para o UDP Ping: ")
    do_udp_ping(destino, QUANTIDADE, TAMANHO_PACOTE)

if __name__ == "__main__":
    main()
