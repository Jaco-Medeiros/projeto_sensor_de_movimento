import tkinter as tk
import socket
import csv
import datetime
from collections import deque
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Configurações de Rede UDP
UDP_IP = "0.0.0.0"  # Escuta em todas as interfaces locais do PC
UDP_PORT = 8080     # A mesma porta configurada na placa STM32

class ServidorMonitorizacao:
    def __init__(self, master):
        self.master = master
        self.master.title("Sistema Central - Monitorização de Carga")
        self.master.geometry("800x600")

        # Configuração do Socket UDP (Não-bloqueante)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((UDP_IP, UDP_PORT))
        self.sock.setblocking(False)

        # Estruturas para o Gráfico (Armazena as últimas 60 leituras)
        self.tempos = deque(maxlen=60)
        self.valores = deque(maxlen=60)

        # Inicialização do Ficheiro de Log (CSV)
        self.ficheiro_csv = "historico_sensor.csv"
        with open(self.ficheiro_csv, mode='a', newline='') as file:
            writer = csv.writer(file)
            # Escreve o cabeçalho se o ficheiro for novo
            writer.writerow(["Timestamp", "Grupo", "Sensor", "Valor Bruto", "Estado Violacao"])

        self.criar_interface()
        self.atualizar_dados() # Inicia o loop de escuta

    def criar_interface(self):
        # Secção Superior (Indicadores e Alertas)
        frame_top = tk.Frame(self.master, pady=15)
        frame_top.pack(fill=tk.X)

        self.lbl_titulo = tk.Label(frame_top, text="ESTADO: A AGUARDAR DADOS...", font=("Arial", 18, "bold"))
        self.lbl_titulo.pack()

        self.lbl_valor = tk.Label(frame_top, text="Valor ADC Atual: ---", font=("Arial", 14))
        self.lbl_valor.pack()

        # Secção Central (Gráfico em tempo real)
        self.fig, self.ax = plt.subplots(figsize=(8, 4), dpi=100)
        self.ax.set_title("Histórico Temporal (PIR AM312)")
        self.ax.set_xlabel("Leituras")
        self.ax.set_ylabel("Tensão Bruta (ADC)")
        self.linha_grafico, = self.ax.plot([], [], 'b-')
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def atualizar_dados(self):
        try:
            # Tenta receber os pacotes UDP enviados pelo kit STM32
            data, addr = self.sock.recvfrom(1024)
            mensagem = data.decode('utf-8').strip()
            
            # Formato esperado enviado pelo C++: GRUPO_X,PIR_AM312,VALOR_BRUTO,ESTADO_ALERTA
            partes = mensagem.split(',')
            if len(partes) == 4:
                grupo, sensor, valor_str, estado_str = partes
                valor_bruto = int(valor_str)
                estado_alerta = int(estado_str)
                
                agora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # 1. Atualizar Alertas Visuais
                self.lbl_valor.config(text=f"Valor ADC Atual: {valor_bruto}")
                
                if estado_alerta == 1:
                    self.lbl_titulo.config(text="ALERTA: VIOLAÇÃO DETETADA NA CARGA!", bg="red", fg="white")
                    self.master.configure(bg="red")
                else:
                    self.lbl_titulo.config(text="ESTADO: SEGURO (Sem movimento)", bg="green", fg="white")
                    self.master.configure(bg="SystemButtonFace")

                # 2. Guardar os dados no Ficheiro CSV de Log
                with open(self.ficheiro_csv, mode='a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow([agora, grupo, sensor, valor_bruto, estado_alerta])

                # 3. Atualizar o Gráfico de Histórico
                self.tempos.append(len(self.tempos))
                self.valores.append(valor_bruto)
                
                self.linha_grafico.set_xdata(range(len(self.tempos)))
                self.linha_grafico.set_ydata(self.valores)
                self.ax.set_xlim(0, max(60, len(self.tempos)))
                self.ax.set_ylim(0, 4200) # Limite máximo do ADC (aprox. 4095)
                self.canvas.draw()

        except BlockingIOError:
            # Passa para o próximo ciclo se não houver novos pacotes na rede
            pass
        except Exception as e:
            print(f"Erro ao processar pacote da rede: {e}")

        # Mantém a janela viva e agenda a próxima verificação a cada 100ms
        self.master.after(100, self.atualizar_dados)

if __name__ == "__main__":
    root = tk.Tk()
    app = ServidorMonitorizacao(root)
    root.mainloop()