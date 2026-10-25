#include "SensorPIR.hpp"
#include <fstream>
#include <iostream>

SensorPIR::SensorPIR(int canal_adc, int limiar_deteccao) : m_limiar(limiar_deteccao) {
    // Mapeia o arquivo lógico do sensor com base no canal descoberto no subsistema IIO
    m_caminho_arquivo = "/sys/bus/iio/devices/iio:device0/in_voltage" + std::to_string(canal_adc) + "_raw";
}

int SensorPIR::lerValorBruto() {
    std::ifstream arquivo(m_caminho_arquivo);
    int valor_lido = 0;
    
    if (arquivo.is_open()) {
        arquivo >> valor_lido;
        arquivo.close();
    } else {
        std::cerr << "Erro: Não foi possível abrir o arquivo do sensor em " << m_caminho_arquivo << std::endl;
    }
    
    return valor_lido;
}

bool SensorPIR::verificarViolacao() {
    return lerValorBruto() > m_limiar;
}