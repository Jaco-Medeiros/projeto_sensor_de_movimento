# Monitoramento Inteligente de Carga \- Sensor de Presença (PIR)

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
* **`main.cpp`** *(Em desenvolvimento)*: Arquivo principal de execução do loop de monitoramento.

### Detalhamento da Classe `SensorPIR`

* **Atributos (Privados):**  
  * `m_caminho_arquivo`: Armazena o caminho do arquivo do canal ADC correspondente.  
  * `m_limiar`: Valor de tensão bruta mínima (offset) para considerar a detecção de movimento.  
* **Métodos (Públicos):**  
  * `SensorPIR(int canal_adc, int limiar_deteccao)`: Construtor que mapeia o canal descoberto no kit (ex: canal 13).  
  * `lerValorBruto()`: Acessa o arquivo lógico no sistema de arquivos do kit e retorna o valor inteiro atual.  
  * `verificarViolacao()`: Compara a leitura com o limiar, retornando `true` se houver intrusão.

## ⚙️ Instruções de Compilação e Execução

Siga os passos abaixo na sua Máquina Virtual Linux para compilar e testar o código no kit STM32MP1:

**1\. Compilação Cruzada (Cross-Compilation):** Utilize a toolchain para compilar a classe e gerar o executável `sensor_app` para a arquitetura ARM:

```sh
arm-buildroot-linux-gnueabihf-g++ src/SensorPIR.cpp main.cpp -I include -o sensor_app
```

*(Nota: Certifique-se de que a toolchain esteja no seu PATH ou utilize o caminho completo até o binário).*

**2\. Transferência para o Kit (via SCP):** Com a placa conectada à rede via cabo Ethernet, envie o executável:

```sh
scp sensor_app root@192.168.42.2:/home/root
```

*(A senha padrão do kit é: `root`)*

**3\. Execução Embarcada:** Acesse o terminal do kit via SSH ou TeraTerm (Serial) e execute o programa gerado:

```sh
ssh root@192.168.42.2
./sensor_app
```

---

*Documentação em atualização constante a cada nova etapa entregue no Google Classroom.*
