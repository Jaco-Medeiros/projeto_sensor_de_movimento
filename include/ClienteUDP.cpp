#ifndef CLIENTE_UDP_HPP
#define CLIENTE_UDP_HPP

#include <string>
#include <netinet/in.h>

class ClienteUDP {
private:
    int m_socket_fd;
    struct sockaddr_in m_endereco_servidor;

public:
    ClienteUDP(const std::string& ip_servidor, int porta);
    ~ClienteUDP();
    bool enviarMensagem(const std::string& mensagem);
};

#endif