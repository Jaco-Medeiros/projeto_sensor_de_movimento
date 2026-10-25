/**
 * @file SensorPIR.hpp
 * @brief Definição da classe SensorPIR para o monitoramento de presença.
 * @details Encapsula a leitura do sensor PIR Digital AM312 através do subsistema IIO do Linux embarcado, visando a detecção de presença humana próxima à carga.
 */

#ifndef SENSOR_PIR_HPP
#define SENSOR_PIR_HPP

#include <string>

/**
 * @brief Classe responsável por gerenciar o sensor de presença (PIR).
 * @details Fornece métodos para inicializar o sensor no canal correto e realizar a leitura dos dados brutos sem o uso de variáveis globais.
 */
class SensorPIR {
private:
    std::string m_caminho_arquivo; //!< Caminho absoluto no sistema de arquivos para o canal ADC correspondente
    int m_limiar;                  //!< Valor de referência para considerar o sensor acionado (presença detectada)

public:
    /**
     * @brief Construtor da classe SensorPIR.
     * @param canal_adc Número do canal ADC correspondente à conexão física no kit (ex: 0, 1, 2).
     * @param limiar_deteccao Tensão bruta mínima para caracterizar uma violação (padrão: 2000).
     */
    SensorPIR(int canal_adc, int limiar_deteccao = 2000);

    /**
     * @brief Realiza a leitura instantânea do valor no arquivo do sensor.
     * @return O valor inteiro lido do arquivo in_voltageX_raw.
     */
    int lerValorBruto();

    /**
     * @brief Verifica se houve detecção de movimento com base no limiar configurado.
     * @return true se o valor lido for maior que o limiar (movimento detectado), false caso contrário.
     */
    bool verificarViolacao();
};

#endif