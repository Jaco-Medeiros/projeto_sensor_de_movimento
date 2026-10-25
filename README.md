# Monitoramento Inteligente de Carga - Sensor de Presença (PIR)

## 📌 Descrição Geral do Projeto

Este projeto faz parte do sistema de **Monitoramento Inteligente de Carga**, desenvolvido em C++ para o kit de desenvolvimento embarcado **STM32MP1 DK1**. O objetivo é garantir a segurança de cargas sensíveis durante o transporte militar.

O escopo deste repositório abrange a integração e controle do **Módulo Sensor de Presença PIR Digital (AM312)**. O sensor é responsável por detectar a presença humana não autorizada próxima à carga. Ao final do projeto, os dados deste módulo serão transmitidos via UDP para um servidor central, compondo a rede de Internet das Coisas (IoT) tática.

## 🛠 Dependências Necessárias

Para compilar, documentar e executar este projeto, o seu ambiente (Máquina Virtual Linux) precisa das seguintes ferramentas:

* **Toolchain de Compilação Cruzada:** `arm-buildroot-linux-gnueabihf_sdk-DK2`
* **Gerador de Documentação:** `Doxygen`
* **Gerador de Gráficos/Diagramas:** `Graphviz`
* **Acesso à Placa:** Cliente `SSH` e `SCP` para transferência via rede.

## 📂 Estrutura do Código e Classes

O sistema foi modelado com foco no encapsulamento orientado a objetos, garantindo a ausência de variáveis globais e facilitando a futura integração.

* **`include/SensorPIR.hpp`**: Arquivo de cabeçalho. Contém a declaração da classe `SensorPIR`, devidamente documentada com Doxygen.
* **`src/SensorPIR.cpp`**: Arquivo de implementação. Realiza a leitura física interagindo com o subsistema IIO do Linux (`/sys/bus/iio/devices/...`).
* **`main.cpp`**: Arquivo principal de execução do loop de monitoramento contínuo.

### Detalhamento da Classe `SensorPIR`

* **Atributos (Privados):**
  * `m_caminho_arquivo`: Armazena o caminho do arquivo do canal ADC correspondente.
  * `m_limiar`: Valor de tensão bruta mínima (offset) para considerar a detecção de movimento.

* **Métodos (Públicos):**
  * `SensorPIR(int canal_adc, int limiar_deteccao)`: Construtor que mapeia o canal descoberto no kit (ex: canal 13).
  * `lerValorBruto()`: Acessa o arquivo lógico no sistema de arquivos do kit e retorna o valor inteiro atual.
  * `verificarViolacao()`: Compara a leitura com o limiar, retornando `true` se houver intrusão.

## ⚙️ Instruções de Compilação e Execução (Entrega 2)

Este sistema foi projetado para ser executado no espaço de usuário Linux do kit STM32MP1-DK1. Siga os passos abaixo na sua Máquina Virtual Linux para compilar e testar o monitoramento no hardware:

### 1. Compilação Cruzada (Cross-Compilation)
No terminal da máquina virtual Linux, utilize a toolchain fornecida para gerar o executável compatível com a arquitetura ARM da placa. Na raiz do projeto, execute:

```bash
arm-buildroot-linux-gnueabihf-g++ src/SensorPIR.cpp main.cpp -I include -o monitoramento_carga
```

*(Nota: Certifique-se de que a toolchain esteja no seu PATH ou utilize o caminho completo até o binário).*

### 2. Transferência para o Kit (via SCP)
Com o kit energizado (cabo na porta PWR_IN) e conectado à rede via cabo Ethernet, envie o arquivo executável gerado para a placa via SCP. Substitua `<ip_da_placa>` pelo IP real do kit (ex: `192.168.42.2`):

```bash
scp monitoramento_carga root@<ip_da_placa>:/home/root
```
*(A senha padrão do usuário root é `root`).*

### 3. Execução no Hardware Embarcado
Acesse o terminal do kit através de uma conexão SSH (ex: `ssh root@192.168.42.2`) ou via cabo serial (TeraTerm) e execute o programa:

```bash
./monitoramento_carga
```
O programa iniciará o monitoramento contínuo em tempo real, exibindo as leituras do canal 13 do ADC e emitindo alertas no console caso o sensor PIR detecte presença humana.

---

