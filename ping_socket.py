import socket
import os
import struct
import time
import select

ICMP_ECHO_REQUEST = 8
TTL_INICIAL = 64

# Quantidade de mensagens a enviar
QUANTIDADE = 10

# Tamanho do payload (em bytes) ➔ padrão do ping é 56 bytes
TAMANHO_PACOTE = 56

TIMEOUT = 1  # Timeout para resposta em segundos

def checksum(source_string):
    sum = 0
    countTo = (len(source_string) // 2) * 2
    count = 0
    while count < countTo:
        thisVal = source_string[count + 1] * 256 + source_string[count]
        sum = sum + thisVal
        sum = sum & 0xffffffff
        count = count + 2
    if countTo < len(source_string):
        sum = sum + source_string[len(source_string) - 1]
        sum = sum & 0xffffffff
    sum = (sum >> 16) + (sum & 0xffff)
    sum = sum + (sum >> 16)
    answer = ~sum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer

def create_packet(id, tamanho_payload):
    header = struct.pack('bbHHh', ICMP_ECHO_REQUEST, 0, 0, id, 1)

    # Cria payload com timestamp (8 bytes) + padding (restante)
    padding_size = max(0, tamanho_payload - 8)  # Garante que não fica negativo
    data = struct.pack('d', time.time()) + bytes(padding_size)

    my_checksum = checksum(header + data)
    header = struct.pack('bbHHh', ICMP_ECHO_REQUEST, 0, socket.htons(my_checksum), id, 1)
    return header + data

def do_ping(dest_addr, count, tamanho_pacote):
    rtts = []
    try:
        dest_ip = socket.gethostbyname(dest_addr)
    except socket.gaierror:
        print(f"Erro: não foi possível resolver {dest_addr}")
        return

    print(f"\nPingando {dest_addr} [{dest_ip}] com {count} mensagens ICMP de {tamanho_pacote} bytes de payload:\n")

    for i in range(1, count + 1):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, TTL_INICIAL)
        except PermissionError:
            print("Erro: este script precisa ser executado como administrador/root!")
            return

        packet_id = os.getpid() & 0xFFFF
        packet = create_packet(packet_id, tamanho_pacote)
        sock.sendto(packet, (dest_ip, 1))

        start_time = time.time()
        ready = select.select([sock], [], [], TIMEOUT)
        if ready[0] == []:
            print(f"Resposta {i}: Timeout")
            sock.close()
            continue

        time_received = time.time()
        rec_packet, addr = sock.recvfrom(1024)
        icmp_header = rec_packet[20:28]
        type, code, checksum_val, p_id, sequence = struct.unpack('bbHHh', icmp_header)

        if p_id == packet_id:
            rtt = (time_received - start_time) * 1000
            rtts.append(rtt)
            ttl = rec_packet[8]
            total_size = len(rec_packet)  # tamanho total recebido (IP + ICMP)
            print(f"Resposta {i}: {total_size} bytes recebidos, RTT = {rtt:.2f} ms, TTL = {ttl}")
        else:
            print(f"Resposta {i}: Pacote inválido")

        sock.close()
        time.sleep(1)

    print("\n--- Estatísticas de ping ---")
    enviados = count
    recebidos = len(rtts)
    perdidos = enviados - recebidos
    perda_pct = (perdidos / enviados) * 100

    print(f"{enviados} pacotes enviados, {recebidos} recebidos, {perda_pct:.0f}% perdidos")

    if rtts:
        print(f"RTT mínimo = {min(rtts):.2f} ms, máximo = {max(rtts):.2f} ms, média = {sum(rtts)/len(rtts):.2f} ms")

def main():
    destino = input("Digite o IP ou hostname para pingar: ")
    do_ping(destino, QUANTIDADE, TAMANHO_PACOTE)

if __name__ == "__main__":
    main()
