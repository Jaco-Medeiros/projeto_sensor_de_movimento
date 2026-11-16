import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import socket
import csv
import os
import shutil
import datetime
from collections import deque
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Configurações de Rede UDP
UDP_IP = "0.0.0.0"
UDP_PORT = 8080

# Paleta de Cores Futurista (Obsidian & Âmbar Tático — Sem Azul)
COR_BG_PRINCIPAL = "#09090B"
COR_CARD = "#141417"
COR_BORDA = "#27272A"
COR_DESTAQUE = "#FFB703"      # Âmbar / Dourado Tático
COR_BOTAO_SEC = "#B45309"     # Âmbar Escuro
COR_TEXTO = "#F4F4F5"
COR_SUBTEXTO = "#A1A1AA"
COR_SEGURO = "#10B981"        # Verde Esmeralda
COR_SEGURO_BG = "#052E16"
COR_ALERTA = "#EF4444"        # Vermelho Alerta
COR_ALERTA_BG = "#450A0A"


class ServidorMonitorizacaoFuturista:
    def __init__(self, master):
        self.master = master
        self.master.title("SENTINEL-OS // MONITORAMENTO TÁTICO DE CARGA")
        self.master.geometry("1040x750")
        self.master.configure(bg=COR_BG_PRINCIPAL)

        # Configuração do Socket UDP (Não-bloqueante)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((UDP_IP, UDP_PORT))
        self.sock.setblocking(False)

        # Estruturas de Telemetria (120 amostras a 500ms = últimos 60s)
        self.tempos = deque(maxlen=120)
        self.valores = deque(maxlen=120)
        self.historico_eventos = deque(maxlen=500)
        self.limiar_alerta = 2000
        self.total_pacotes = 0
        self.total_alertas = 0

        # Rastreamento explícito de data/hora da última presença e não-presença
        self.ultima_presenca_dt = "Nenhum registo"
        self.ultima_segura_dt = "Nenhum registo"

        # Referências da janela de histórico em tempo real
        self.janela_historico = None
        self.tree_historico = None
        self.lbl_hist_presenca = None
        self.lbl_hist_seguro = None

        # Ficheiro de log automático contínuo
        self.ficheiro_csv = "historico_sensor.csv"
        self._inicializar_csv()

        self.criar_interface()
        self.atualizar_dados()

    def _inicializar_csv(self):
        if not os.path.exists(self.ficheiro_csv):
            with open(self.ficheiro_csv, mode='w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerow(["Timestamp", "Grupo", "Sensor", "Valor_ADC", "Estado_Violacao"])
        else:
            # Carrega histórico prévio existente no CSV
            try:
                with open(self.ficheiro_csv, mode='r', newline='', encoding='utf-8') as file:
                    reader = csv.reader(file)
                    next(reader, None)
                    for row in reader:
                        if len(row) == 5:
                            ts, grp, sns, val, est = row
                            viol = (est == "1")
                            status_txt = "PRESENÇA CONFIRMADA" if viol else "SEGURO (SEM PRESENÇA)"
                            self.historico_eventos.append((ts, grp, sns, val, status_txt, viol))
                            if viol:
                                self.ultima_presenca_dt = ts
                            else:
                                self.ultima_segura_dt = ts
            except Exception:
                pass

    def criar_interface(self):
        # --- CABEÇALHO HUD ---
        header = tk.Frame(self.master, bg=COR_CARD, highlightbackground=COR_DESTAQUE, highlightthickness=1, pady=10, padx=15)
        header.pack(fill=tk.X, padx=16, pady=(14, 8))

        tk.Label(
            header,
            text="◈ SENTINEL-OS // TELEMETRIA STM32MP1-DK1",
            font=("Consolas", 14, "bold"),
            fg=COR_DESTAQUE,
            bg=COR_CARD
        ).pack(side=tk.LEFT)

        self.lbl_conexao = tk.Label(
            header,
            text=f"● UDP ATIVO [0.0.0.0:{UDP_PORT}]",
            font=("Consolas", 10, "bold"),
            fg=COR_SEGURO,
            bg=COR_CARD
        )
        self.lbl_conexao.pack(side=tk.RIGHT)

        # --- BANNER DE STATUS PRINCIPAL ---
        self.banner_status = tk.Frame(
            self.master,
            bg=COR_CARD,
            highlightbackground=COR_BORDA,
            highlightthickness=2,
            pady=14
        )
        self.banner_status.pack(fill=tk.X, padx=16, pady=6)

        self.lbl_status_principal = tk.Label(
            self.banner_status,
            text="[ AGUARDANDO SINAL DO SENSOR PIR AM312 ]",
            font=("Consolas", 18, "bold"),
            fg=COR_DESTAQUE,
            bg=COR_CARD
        )
        self.lbl_status_principal.pack()

        self.lbl_substatus = tk.Label(
            self.banner_status,
            text="NÓ: ---  |  SENSOR: PIR_AM312  |  ÚLTIMA SINCRONIZAÇÃO: --:--:--",
            font=("Consolas", 10),
            fg=COR_SUBTEXTO,
            bg=COR_CARD
        )
        self.lbl_substatus.pack(pady=(4, 0))

        # --- CARTÕES DE TELEMETRIA (KPIs) ---
        grid_cards = tk.Frame(self.master, bg=COR_BG_PRINCIPAL)
        grid_cards.pack(fill=tk.X, padx=16, pady=6)
        grid_cards.columnconfigure((0, 1, 2, 3), weight=1)

        self.lbl_card_adc = self._criar_card(grid_cards, 0, "LEITURA BRUTA (ADC)", "00000", COR_DESTAQUE)
        self.lbl_card_limiar = self._criar_card(grid_cards, 1, "LIMIAR DE DISPARO", str(self.limiar_alerta), "#F97316")
        self.lbl_card_pacotes = self._criar_card(grid_cards, 2, "PACOTES RECEBIDOS", "0", COR_TEXTO)
        self.lbl_card_alertas = self._criar_card(grid_cards, 3, "VIOLAÇÕES DETETADAS", "0", COR_ALERTA)

        # --- BARRA DE COMANDO, HISTÓRICO AO VIVO E EXPORTAÇÃO ---
        barra_cmd = tk.Frame(self.master, bg=COR_CARD, highlightbackground=COR_BORDA, highlightthickness=1, pady=8, padx=12)
        barra_cmd.pack(fill=tk.X, padx=16, pady=6)

        tk.Label(
            barra_cmd,
            text="CALIBRAR LIMIAR ADC:",
            font=("Consolas", 10, "bold"),
            fg=COR_SUBTEXTO,
            bg=COR_CARD
        ).pack(side=tk.LEFT, padx=(0, 8))

        self.entry_limiar = tk.Entry(
            barra_cmd,
            width=10,
            font=("Consolas", 11, "bold"),
            bg=COR_BG_PRINCIPAL,
            fg=COR_DESTAQUE,
            insertbackground=COR_DESTAQUE,
            relief=tk.FLAT,
            highlightbackground=COR_DESTAQUE,
            highlightthickness=1
        )
        self.entry_limiar.insert(0, str(self.limiar_alerta))
        self.entry_limiar.pack(side=tk.LEFT, padx=4, ipady=3)

        tk.Button(
            barra_cmd,
            text="APLICAR",
            command=self.atualizar_limiar,
            font=("Consolas", 10, "bold"),
            bg=COR_BOTAO_SEC,
            fg="white",
            activebackground=COR_DESTAQUE,
            activeforeground="black",
            relief=tk.FLAT,
            padx=12,
            pady=3,
            cursor="hand2"
        ).pack(side=tk.LEFT, padx=8)

        tk.Button(
            barra_cmd,
            text="⇩ EXPORTAR LOG (.CSV)",
            command=self.exportar_csv,
            font=("Consolas", 10, "bold"),
            bg="#047857",
            fg="white",
            activebackground=COR_SEGURO,
            activeforeground="black",
            relief=tk.FLAT,
            padx=12,
            pady=3,
            cursor="hand2"
        ).pack(side=tk.RIGHT, padx=(6, 0))

        tk.Button(
            barra_cmd,
            text="☰ HISTÓRICO EM TEMPO REAL",
            command=self.abrir_janela_historico,
            font=("Consolas", 10, "bold"),
            bg=COR_DESTAQUE,
            fg="#09090B",
            activebackground="#FDE047",
            activeforeground="#09090B",
            relief=tk.FLAT,
            padx=14,
            pady=3,
            cursor="hand2"
        ).pack(side=tk.RIGHT, padx=6)

        # --- GRÁFICO TEMPORAL FUTURISTA ---
        frame_grafico = tk.Frame(self.master, bg=COR_CARD, highlightbackground=COR_BORDA, highlightthickness=1, padx=6, pady=6)
        frame_grafico.pack(fill=tk.BOTH, expand=True, padx=16, pady=(6, 14))

        self.fig, self.ax = plt.subplots(figsize=(9, 4), dpi=100)
        self.fig.patch.set_facecolor(COR_CARD)
        self.ax.set_facecolor(COR_BG_PRINCIPAL)

        self.ax.set_title("ESPECTRO TEMPORAL DO SENSOR PIR AM312 (ÚLTIMOS 60s)", color=COR_DESTAQUE, fontsize=11, fontweight="bold", pad=10)
        self.ax.set_xlabel("JANELA DE TEMPO (HH:MM:SS)", color=COR_SUBTEXTO, fontsize=9)
        self.ax.set_ylabel("AMPLITUDE ADC", color=COR_SUBTEXTO, fontsize=9)
        self.ax.tick_params(colors=COR_SUBTEXTO, labelsize=8)

        for spine in self.ax.spines.values():
            spine.set_edgecolor(COR_BORDA)

        self.ax.grid(True, color="#27272A", linestyle=":", linewidth=0.8)
        self.linha_grafico, = self.ax.plot([], [], color=COR_DESTAQUE, linewidth=2.2, label="Sinal PIR (ADC)")
        self.linha_limite = self.ax.axhline(y=self.limiar_alerta, color="#F97316", linestyle="--", linewidth=1.2, label="Limiar Crítico")
        self.preenchimento = None

        legenda = self.ax.legend(loc="upper right", facecolor=COR_CARD, edgecolor=COR_BORDA, fontsize=8)
        for text in legenda.get_texts():
            text.set_color(COR_TEXTO)

        self.canvas = FigureCanvasTkAgg(self.fig, master=frame_grafico)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def _criar_card(self, parent, col, titulo, valor_inicial, cor_valor):
        card = tk.Frame(parent, bg=COR_CARD, highlightbackground=COR_BORDA, highlightthickness=1, pady=10, padx=12)
        card.grid(row=0, column=col, sticky="nsew", padx=4)

        tk.Label(card, text=titulo, font=("Consolas", 9, "bold"), fg=COR_SUBTEXTO, bg=COR_CARD).pack(anchor="w")
        lbl_val = tk.Label(card, text=valor_inicial, font=("Consolas", 18, "bold"), fg=cor_valor, bg=COR_CARD)
        lbl_val.pack(anchor="w", pady=(4, 0))
        return lbl_val

    def abrir_janela_historico(self):
        # Se a janela já estiver aberta, apenas traz para frente
        if self.janela_historico is not None and self.janela_historico.winfo_exists():
            self.janela_historico.lift()
            return

        self.janela_historico = tk.Toplevel(self.master)
        self.janela_historico.title("SENTINEL-OS // HISTÓRICO DE EVENTOS EM TEMPO REAL")
        self.janela_historico.geometry("860x520")
        self.janela_historico.configure(bg=COR_BG_PRINCIPAL)

        # Painel Superior: Última Presença vs. Último Estado Seguro
        painel_resumo = tk.Frame(
            self.janela_historico,
            bg=COR_CARD,
            highlightbackground=COR_DESTAQUE,
            highlightthickness=1,
            pady=12,
            padx=15
        )
        painel_resumo.pack(fill=tk.X, padx=14, pady=(12, 8))

        self.lbl_hist_presenca = tk.Label(
            painel_resumo,
            text=f"⚠ ÚLTIMA PRESENÇA CONFIRMADA: {self.ultima_presenca_dt}",
            font=("Consolas", 11, "bold"),
            fg=COR_ALERTA,
            bg=COR_CARD
        )
        self.lbl_hist_presenca.pack(anchor="w", pady=(0, 4))

        self.lbl_hist_seguro = tk.Label(
            painel_resumo,
            text=f"✔ ÚLTIMA LEITURA SEM PRESENÇA: {self.ultima_segura_dt}",
            font=("Consolas", 11, "bold"),
            fg=COR_SEGURO,
            bg=COR_CARD
        )
        self.lbl_hist_seguro.pack(anchor="w")

        # Estilo escuro da tabela Treeview
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(
            "DarkHUD.Treeview",
            background=COR_CARD,
            foreground=COR_TEXTO,
            fieldbackground=COR_CARD,
            bordercolor=COR_BORDA,
            rowheight=26,
            font=("Consolas", 10)
        )
        style.configure(
            "DarkHUD.Treeview.Heading",
            background="#27272A",
            foreground=COR_DESTAQUE,
            bordercolor=COR_BORDA,
            font=("Consolas", 10, "bold")
        )
        style.map("DarkHUD.Treeview", background=[("selected", "#3F3F46")])

        frame_tabela = tk.Frame(self.janela_historico, bg=COR_CARD, highlightbackground=COR_BORDA, highlightthickness=1)
        frame_tabela.pack(fill=tk.BOTH, expand=True, padx=14, pady=(4, 14))

        colunas = ("timestamp", "grupo", "sensor", "adc", "status")
        self.tree_historico = ttk.Treeview(
            frame_tabela,
            columns=colunas,
            show="headings",
            style="DarkHUD.Treeview"
        )

        self.tree_historico.heading("timestamp", text="DATA / HORA")
        self.tree_historico.heading("grupo", text="GRUPO")
        self.tree_historico.heading("sensor", text="SENSOR")
        self.tree_historico.heading("adc", text="VALOR ADC")
        self.tree_historico.heading("status", text="ESTADO DETETADO")

        self.tree_historico.column("timestamp", width=180, anchor="center")
        self.tree_historico.column("grupo", width=110, anchor="center")
        self.tree_historico.column("sensor", width=120, anchor="center")
        self.tree_historico.column("adc", width=110, anchor="center")
        self.tree_historico.column("status", width=260, anchor="center")

        self.tree_historico.tag_configure("violacao", foreground=COR_ALERTA, background="#2A0808")
        self.tree_historico.tag_configure("seguro", foreground=COR_SEGURO, background=COR_CARD)

        scrollbar = ttk.Scrollbar(frame_tabela, orient=tk.VERTICAL, command=self.tree_historico.yview)
        self.tree_historico.configure(yscrollcommand=scrollbar.set)

        self.tree_historico.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Popula com os eventos acumulados (mais recentes no topo)
        for ev in reversed(self.historico_eventos):
            ts, grp, sns, val, status_txt, viol = ev
            tag = "violacao" if viol else "seguro"
            self.tree_historico.insert("", tk.END, values=(ts, grp, sns, val, status_txt), tags=(tag,))

    def atualizar_limiar(self):
        try:
            novo_valor = int(self.entry_limiar.get())
            self.limiar_alerta = novo_valor
            self.lbl_card_limiar.config(text=str(self.limiar_alerta))
            self.linha_limite.set_ydata([self.limiar_alerta, self.limiar_alerta])
            self.canvas.draw()
            messagebox.showinfo("Calibração Concluída", f"Limiar atualizado para {self.limiar_alerta} ADC.")
        except ValueError:
            messagebox.showerror("Erro de Parâmetro", "Insira um valor numérico inteiro válido.")

    def exportar_csv(self):
        destino = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("Arquivos CSV", "*.csv"), ("Arquivos de Log", "*.log")],
            initialfile=f"telemetria_pir_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        if destino:
            shutil.copy(self.ficheiro_csv, destino)
            messagebox.showinfo("Log Exportado", f"Registo histórico salvo em:\n{destino}")

    def atualizar_dados(self):
        try:
            data, _ = self.sock.recvfrom(1024)
            mensagem = data.decode('utf-8').strip()
            partes = mensagem.split(',')

            if len(partes) == 4:
                grupo, sensor, valor_str, estado_str = partes
                valor_bruto = int(valor_str)
                estado_kit = int(estado_str)

                agora_full = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                hora_curta = datetime.datetime.now().strftime("%H:%M:%S")

                violacao = (estado_kit == 1) or (valor_bruto > self.limiar_alerta)
                self.total_pacotes += 1
                if violacao:
                    self.total_alertas += 1
                    self.ultima_presenca_dt = agora_full
                    status_txt = "PRESENÇA CONFIRMADA"
                else:
                    self.ultima_segura_dt = agora_full
                    status_txt = "SEGURO (SEM PRESENÇA)"

                # Regista no buffer em memória e atualiza a janela de histórico se estiver aberta
                self.historico_eventos.append((agora_full, grupo, sensor, valor_bruto, status_txt, violacao))
                if self.janela_historico is not None and self.janela_historico.winfo_exists():
                    self.lbl_hist_presenca.config(text=f"⚠ ÚLTIMA PRESENÇA CONFIRMADA: {self.ultima_presenca_dt}")
                    self.lbl_hist_seguro.config(text=f"✔ ÚLTIMA LEITURA SEM PRESENÇA: {self.ultima_segura_dt}")
                    tag = "violacao" if violacao else "seguro"
                    self.tree_historico.insert("", 0, values=(agora_full, grupo, sensor, valor_bruto, status_txt), tags=(tag,))

                # Atualiza KPIs
                self.lbl_card_adc.config(
                    text=f"{valor_bruto:05d}",
                    fg=COR_ALERTA if violacao else COR_SEGURO
                )
                self.lbl_card_pacotes.config(text=str(self.total_pacotes))
                self.lbl_card_alertas.config(text=str(self.total_alertas))

                # Atualiza Banner Principal
                self.lbl_substatus.config(
                    text=f"NÓ: {grupo}  |  SENSOR: {sensor}  |  ÚLTIMA SINCRONIZAÇÃO: {agora_full}"
                )

                if violacao:
                    self.banner_status.config(bg=COR_ALERTA_BG, highlightbackground=COR_ALERTA)
                    self.lbl_status_principal.config(
                        text="⚠ ALERTA CRÍTICO: PRESENÇA CONFIRMADA NA CARGA ⚠",
                        fg=COR_ALERTA,
                        bg=COR_ALERTA_BG
                    )
                    self.lbl_substatus.config(bg=COR_ALERTA_BG, fg="#FCA5A5")
                    cor_linha = COR_ALERTA
                else:
                    self.banner_status.config(bg=COR_SEGURO_BG, highlightbackground=COR_SEGURO)
                    self.lbl_status_principal.config(
                        text="✔ PERÍMETRO SEGURO // NENHUMA INTRUSÃO DETETADA",
                        fg=COR_SEGURO,
                        bg=COR_SEGURO_BG
                    )
                    self.lbl_substatus.config(bg=COR_SEGURO_BG, fg="#86EFAC")
                    cor_linha = COR_DESTAQUE

                # Gravação Contínua em Log CSV
                with open(self.ficheiro_csv, mode='a', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow([agora_full, grupo, sensor, valor_bruto, 1 if violacao else 0])

                # Atualização do Gráfico Temporal
                self.tempos.append(hora_curta)
                self.valores.append(valor_bruto)

                indices = list(range(len(self.tempos)))
                valores_lista = list(self.valores)

                self.linha_grafico.set_xdata(indices)
                self.linha_grafico.set_ydata(valores_lista)
                self.linha_grafico.set_color(cor_linha)

                if self.preenchimento:
                    self.preenchimento.remove()
                self.preenchimento = self.ax.fill_between(indices, valores_lista, color=cor_linha, alpha=0.18)

                self.ax.set_xlim(0, max(10, len(self.tempos) - 1))
                self.ax.set_ylim(-2000, 70000)

                if len(self.tempos) > 1:
                    passo = max(1, len(self.tempos) // 6)
                    ticks = indices[::passo]
                    labels = [list(self.tempos)[i] for i in ticks]
                    self.ax.set_xticks(ticks)
                    self.ax.set_xticklabels(labels, rotation=15)

                self.canvas.draw()

        except BlockingIOError:
            pass
        except Exception as e:
            print(f"[ERRO TELEMETRIA]: {e}")

        self.master.after(100, self.atualizar_dados)


if __name__ == "__main__":
    root = tk.Tk()
    app = ServidorMonitorizacaoFuturista(root)
    root.mainloop()