#include <iostream>
#include <unistd.h>
#include <string>
#include "SensorPIR.hpp"
#include "ClienteUDP.hpp"

int main() {
    // Altere para o IP e porta reais do computador que servirá como servidor central
    std::string ip_servidor = "10.0.2.15"; 
    int porta_servidor = 8080;

    SensorPIR sensorCarga(13);
    ClienteUDP cliente(ip_servidor, porta_servidor);

    std::cout << "Iniciando monitoramento e transmissao UDP para " << ip_servidor << ":" << porta_servidor << std::endl;

    while (true) {
        int valorBruto = sensorCarga.lerValorBruto();
        bool violacao = sensorCarga.verificarViolacao();
        int estado = violacao ? 1 : 0;

        // Protocolo CSV: ID_GRUPO,ID_SENSOR,VALOR_BRUTO,ESTADO_ALERTA
        std::string mensagem = "GRUPO_X,PIR_AM312," + std::to_string(valorBruto) + "," + std::to_string(estado);
        
        cliente.enviarMensagem(mensagem);

        std::cout << "Enviado: " << mensagem << std::endl;
        usleep(500000); // 500ms
    }

    return 0;
}
