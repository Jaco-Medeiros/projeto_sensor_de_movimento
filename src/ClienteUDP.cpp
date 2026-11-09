#include "ClienteUDP.hpp"
#include <arpa/inet.h>
#include <unistd.h>
#include <iostream>
#include <cstring>

ClienteUDP::ClienteUDP(const std::string& ip_servidor, int porta) {
    m_socket_fd = socket(AF_INET, SOCK_DGRAM, 0);
    if (m_socket_fd < 0) {
        std::cerr << "Erro ao criar socket UDP" << std::endl;
        return;
    }

    memset(&m_endereco_servidor, 0, sizeof(m_endereco_servidor));
    m_endereco_servidor.sin_family = AF_INET;
    m_endereco_servidor.sin_port = htons(porta);
    inet_pton(AF_INET, ip_servidor.c_str(), &m_endereco_servidor.sin_addr);
}

ClienteUDP::~ClienteUDP() {
    if (m_socket_fd >= 0) {
        close(m_socket_fd);
    }
}

bool ClienteUDP::enviarMensagem(const std::string& mensagem) {
    if (m_socket_fd < 0) return false;
    
    ssize_t bytes_enviados = sendto(m_socket_fd, mensagem.c_str(), mensagem.length(), 0,
                                    (struct sockaddr*)&m_endereco_servidor, sizeof(m_endereco_servidor));
    return bytes_enviados >= 0;
}