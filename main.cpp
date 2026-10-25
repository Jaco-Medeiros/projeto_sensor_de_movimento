#include <iostream>
#include <unistd.h> // Necessário para a função usleep() no Linux
#include "SensorPIR.hpp"

int main() {
    std::cout << "Iniciando sistema de monitoramento tatico de carga..." << std::endl;
    std::cout << "Inicializando Sensor PIR Digital no Canal 13." << std::endl;
    std::cout << "---------------------------------------------------" << std::endl;
    
    // Instancia o objeto do sensor informando o canal 13 descoberto fisicamente
    SensorPIR sensorCarga(13);

    // Loop infinito para leitura contínua e em tempo real
    while (true) {
        int valorBruto = sensorCarga.lerValorBruto();
        bool violacao = sensorCarga.verificarViolacao();

        std::cout << "ADC [Canal 13]: " << valorBruto << " \t| Estado: ";
        
        if (violacao) {
            std::cout << "[ALERTA CRITICO] Presenca humana detectada! Possivel violacao." << std::endl;
        } else {
            std::cout << "Seguro. Nenhuma movimentacao." << std::endl;
        }

        // Pausa de 500ms (500000 microssegundos) entre leituras para estabilidade do loop
        usleep(500000);
    }

    return 0;
}