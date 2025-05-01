import time
from ping3 import ping

def main():
    destino = input("Digite o IP ou hostname para pingar: ")
    tentativas = 10
    rtts = []
    ttls = []

    print(f"\nPingando {destino} com {tentativas} mensagens ICMP:\n")

    for i in range(1, tentativas + 1):
        result = ping(destino, unit='ms', timeout=1)

        if result is None:
            print(f"Resposta {i}: Timeout")
        else:
            rtt = result
            rtts.append(rtt)
            print(f"Resposta {i}: RTT = {rtt:.2f} ms")

        time.sleep(1)

    print("\n--- Estatísticas de ping ---")
    enviados = tentativas
    recebidos = len(rtts)
    perdidos = enviados - recebidos
    perda_pct = (perdidos / enviados) * 100

    print(f"{enviados} pacotes enviados, {recebidos} recebidos, {perda_pct:.0f}% perdidos")

    if rtts:
        print(f"RTT mínimo = {min(rtts):.2f} ms, máximo = {max(rtts):.2f} ms, média = {sum(rtts)/len(rtts):.2f} ms")

if __name__ == "__main__":
    main()
