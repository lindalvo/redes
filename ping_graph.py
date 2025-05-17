import streamlit as st
import socket
import time
import select
import os
import pandas as pd
import matplotlib.pyplot as plt

# --- Interface Streamlit ---
st.set_page_config(page_title="Ping UDP - Redes de Computadores", layout="centered")
st.title("📡 Redes de Computadores")

# Entradas do usuário
dest = st.text_input("Endereço do servidor UDP", value="127.0.0.1")
port = st.number_input("Porta do servidor UDP", min_value=1024, max_value=65535, value=12000)
delay_max = st.slider("Delay máximo (timeout) para resposta (segundos)", 0.1, 5.0, 1.0, step=0.1)
packet_size = st.slider("Tamanho da mensagem UDP (bytes)", 8, 1400, 64, step=16)
num_pings = st.slider("Número de mensagens de ping", 1, 20, 5)
run_ping = st.button("Iniciar Ping")

# Execução
if run_ping:
    try:
        st.write(f"Enviando pings UDP para {dest}:{port} com {packet_size} bytes...")

        rtts = []
        placeholder = st.empty()

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(delay_max)

            for seq in range(num_pings):
                message = f"PING {seq} {time.time()}".encode()
                padding = b'x' * (packet_size - len(message)) if packet_size > len(message) else b''
                packet = message + padding
                start = time.time()

                try:
                    sock.sendto(packet, (dest, port))
                    ready = select.select([sock], [], [], delay_max)

                    if not ready[0]:
                        st.warning(f"Ping {seq + 1}: Timeout")
                        rtts.append(None)
                        continue

                    data, addr = sock.recvfrom(2048)
                    end = time.time()

                    rtt = (end - start) * 1000
                    rtts.append(rtt)
                    st.success(f"Ping {seq + 1} de {addr[0]}: RTT = {rtt:.2f} ms")

                except socket.timeout:
                    st.warning(f"Ping {seq + 1}: Timeout")
                    rtts.append(None)

                # Atualiza gráfico
                df = pd.DataFrame({'Ping': list(range(1, len(rtts)+1)), 'RTT (ms)': rtts})
                plt.figure(figsize=(6,3))
                plt.plot(df['Ping'], df['RTT (ms)'], marker='o', label='RTT (ms)')
                lost_pings = df['RTT (ms)'].isna()
                plt.scatter(df['Ping'][lost_pings], [0]*lost_pings.sum(), color='red', marker='x', s=100, label='Pacote perdido')
                plt.ylim(bottom=0)
                plt.xlabel('Ping')
                plt.ylabel('RTT (ms)')
                plt.legend()
                placeholder.pyplot(plt.gcf())
                plt.clf()

                time.sleep(1)

        if not any(r is not None for r in rtts):
            st.error("Nenhuma resposta recebida.")
        else:
            rtt_ok = [r for r in rtts if r is not None]
            st.subheader("📊 Estatísticas")
            st.write(f"RTT mínimo: {min(rtt_ok):.2f} ms")
            st.write(f"RTT máximo: {max(rtt_ok):.2f} ms")
            st.write(f"RTT médio: {sum(rtt_ok) / len(rtt_ok):.2f} ms")

    except Exception as e:
        st.error(f"Erro: {e}")
