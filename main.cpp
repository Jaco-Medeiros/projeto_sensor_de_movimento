#include <iostream>
#include <unistd.h>
#include <string>
#include "SensorPIR.hpp"
#include "ClienteUDP.hpp"

int main() {
    // Altere para o IP da sua máquina virtual/servidor na rede da placa
    std::string ip_servidor = "192.168.42.10"; 
    int porta_servidor = 8080;

    SensorPIR sensorCarga(13);
    ClienteUDP cliente(ip_servidor, porta_servidor);

    std::cout << "Iniciando monitoramento e transmissao UDP para " << ip_servidor << ":" << porta_servidor << std::endl;

    while (true) {
        int valorBruto = sensorCarga.lerValorBruto();
        bool violacao = sensorCarga.verificarViolacao(); // Verifica se passou do limiar (ex: 2000)
        int estado = violacao ? 1 : 0;

        // Protocolo CSV: ID_GRUPO,ID_SENSOR,VALOR_BRUTO,ESTADO_ALERTA
        std::string mensagem = "GRUPO_X,PIR_AM312," + std::to_string(valorBruto) + "," + std::to_string(estado);
        
        // Envia o pacote UDP para o servidor central
        cliente.enviarMensagem(mensagem);

        // Exibe no terminal do kit com base no estado da violação
        if (violacao) {
            std::cout << "Enviado: " << mensagem << " | [ALERTA] Presenca confirmada!" << std::endl;
        } else {
            std::cout << "Enviado: " << mensagem << " | Estado: Seguro (Sem movimento)" << std::endl;
        }

        usleep(500000); // Intervalo de 500ms entre as leituras
    }

    return 0;
}