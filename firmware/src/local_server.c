#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <dirent.h>

#define PORT 8080

void *run_local_server(void *arg) {
    int server_fd, new_socket;
    struct sockaddr_in address;
    int opt = 1;
    int addrlen = sizeof(address);
    char buffer[1024] = {0};
    
    if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) == 0) {
        perror("socket failed");
        return NULL;
    }
    
    if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt))) {
        perror("setsockopt");
        return NULL;
    }
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(PORT);
    
    if (bind(server_fd, (struct sockaddr *)&address, sizeof(address)) < 0) {
        perror("bind failed");
        return NULL;
    }
    if (listen(server_fd, 3) < 0) {
        perror("listen");
        return NULL;
    }
    
    printf("Local HTTP server running on port %d (GET /locked_incidents)\n", PORT);
    
    while(1) {
        if ((new_socket = accept(server_fd, (struct sockaddr *)&address, (socklen_t*)&addrlen)) < 0) {
            perror("accept");
            continue;
        }
        
        memset(buffer, 0, sizeof(buffer));
        read(new_socket, buffer, 1024);
        
        if (strncmp(buffer, "GET /locked_incidents", 21) == 0) {
            DIR *d;
            struct dirent *dir;
            d = opendir(".");
            
            char response_body[2048] = "{\n  \"incidents\": [\n";
            int count = 0;
            if (d) {
                while ((dir = readdir(d)) != NULL) {
                    if (strncmp(dir->d_name, "incident_", 9) == 0 && strstr(dir->d_name, ".mp4")) {
                        if (count > 0) strcat(response_body, ",\n");
                        strcat(response_body, "    \"");
                        strcat(response_body, dir->d_name);
                        strcat(response_body, "\"");
                        count++;
                    }
                }
                closedir(d);
            }
            strcat(response_body, "\n  ]\n}");
            
            char http_header[1024];
            sprintf(http_header, "HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: %lu\r\nConnection: close\r\n\r\n", strlen(response_body));
            
            send(new_socket, http_header, strlen(http_header), 0);
            send(new_socket, response_body, strlen(response_body), 0);
        } else if (strncmp(buffer, "DELETE /", 8) == 0) {
            char filename[256] = {0};
            // format: DELETE /incident_XYZ.mp4 HTTP/1.1
            sscanf(buffer, "DELETE /%255s HTTP", filename);
            
            if (strncmp(filename, "incident_", 9) == 0 && strstr(filename, ".mp4")) {
                if (remove(filename) == 0) {
                    char *ok = "HTTP/1.1 200 OK\r\nContent-Length: 0\r\nConnection: close\r\n\r\n";
                    send(new_socket, ok, strlen(ok), 0);
                    printf("Deleted %s\n", filename);
                } else {
                    char *err = "HTTP/1.1 500 Internal Server Error\r\nContent-Length: 0\r\nConnection: close\r\n\r\n";
                    send(new_socket, err, strlen(err), 0);
                    perror("remove failed");
                }
            } else {
                char *not_found = "HTTP/1.1 403 Forbidden\r\nContent-Length: 0\r\nConnection: close\r\n\r\n";
                send(new_socket, not_found, strlen(not_found), 0);
            }
        } else {
            char *not_found = "HTTP/1.1 404 Not Found\r\nContent-Length: 0\r\nConnection: close\r\n\r\n";
            send(new_socket, not_found, strlen(not_found), 0);
        }
        
        close(new_socket);
    }
    return NULL;
}