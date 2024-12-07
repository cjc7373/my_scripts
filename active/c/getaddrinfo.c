// example:
// $ ./a.out www.baidu.com
// 36.155.132.76 family: 2 socktype: 1 protocol: 6
// 36.155.132.3 family: 2 socktype: 1 protocol: 6
// 2409:8c20:6:1d55:0:ff:b09c:7d77 family: 10 socktype: 1 protocol: 6
// 2409:8c20:6:1135:0:ff:b027:210c family: 10 socktype: 1 protocol: 6

#include <netdb.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>

void wrapper(char *address, int ai_family) {
    struct addrinfo *listp, *p, hints;
    memset(&hints, 0, sizeof(struct addrinfo));
    hints.ai_family = ai_family;
    hints.ai_socktype = SOCK_STREAM;
    int rc;
    if ((rc = getaddrinfo(address, NULL, &hints, &listp)) != 0) {
        fprintf(stderr, "getaddrinfo error (ai_family: %d): %s\n", ai_family,
                gai_strerror(rc));
        return;
    }

    char buf[1024];
    for (p = listp; p != NULL; p = p->ai_next) {
        getnameinfo(p->ai_addr, p->ai_addrlen, buf, 1024, NULL, 0, 0);
        printf("%s family: %d socktype: %d protocol: %d\n", buf, p->ai_family,
               p->ai_socktype, p->ai_protocol);
    }

    freeaddrinfo(listp);
}

int main(int argc, char **argv) {
    if (argc != 2) {
        fprintf(stderr, "usage: %s <domain name>\n", argv[0]);
        exit(0);
    }

    wrapper(argv[1], AF_INET);
    wrapper(argv[1], AF_INET6);
}
