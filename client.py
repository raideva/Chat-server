import socket
import select
import errno
import sys

import pygame

HEADER_LENGTH = 10

IP = "127.0.0.1"
PORT = 1234
my_username = input("Name: ")

# Create a socket
# socket.AF_INET - address family, IPv4, some otehr possible are AF_INET6, AF_BLUETOOTH, AF_UNIX
# socket.SOCK_STREAM - TCP, conection-based, socket.SOCK_DGRAM - UDP, connectionless, datagrams, socket.SOCK_RAW - raw IP packets
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to a given ip and port
client_socket.connect((IP, PORT))

# Set connection to non-blocking state, so .recv() call won;t block, just return some exception we'll handle
client_socket.setblocking(False)

# Prepare username and header and send them
# We need to encode username to bytes, then count number of bytes and prepare header of fixed size, that we encode to bytes as well
username = my_username.encode('utf-8')
username_header = f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')
client_socket.send(username_header + username)


pygame.init()

screen = pygame.display.set_mode([1100, 700])

base_font = pygame.font.Font(None, 32)
head_font = pygame.font.Font(None, 64)

color_active = pygame.Color('lightskyblue3')

color_passive = pygame.Color('chartreuse4')

def send_message(msg):
    if not len(msg):
        return
    message = msg.encode('utf-8')
    message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
    client_socket.send(message_header + message)
    mes_store.append(f'{my_username} > {inp[0][0]}')
    inp[0][0] = ""

st4 = head_font.render("Chat Server", True, (0, 170, 170))

inp = []
user_text = ''
x = 300
y = 135
input_rect = pygame.Rect(x, y, 140, 32)
color = color_passive
inp.append([user_text, input_rect, color, False])


v = []

def c_text():
    text = base_font.render('Message : ', True, (0, 0, 0))
    textRect = text.get_rect()
    textRect.center = (200, 150)
    v.append([text, textRect])

c_text()

mes_store = []

def blit_text(surface, text, pos, font, color=pygame.Color('black')):
    text.reverse()
    words = [word.split(' ') for word in text]  # 2D array where each row is a list of words.
    space = font.size(' ')[0]  # The width of a space.
    max_width, max_height = surface.get_size()
    x, y = pos
    for line in words:
        for word in line:
            word_surface = font.render(word, 0, color)
            word_width, word_height = word_surface.get_size()
            if x + word_width >= max_width:
                x = pos[0]  # Reset the x.
                y += word_height  # Start on new row.
            surface.blit(word_surface, (x, y))
            x += word_width + space
        x = pos[0]  # Reset the x.
        y += word_height

t = base_font.render("Send Message", True, (170, 170, 170))

while True:

    screen.fill((51, 51, 255))

    screen.blit(st4, (380, 30))

    for i in range(1):
        screen.blit(v[i][0], v[i][1])

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        mouse = pygame.mouse.get_pos()

        if event.type == pygame.MOUSEBUTTONDOWN:
            if inp[0][1].collidepoint(event.pos):
                inp[0][3] = True
            else:
                inp[0][3] = False
            if 430 <= mouse[0] <= 640 and 190 <= mouse[1] <= 230:
                send_message(inp[0][0])

        if event.type == pygame.KEYDOWN:
            if inp[0][3]:
                if event.key == pygame.K_BACKSPACE:
                    inp[0][0] = inp[0][0][:-1]
                elif event.key == pygame.K_RETURN:
                    if len(inp[0][0]) > 0:
                        send_message(inp[0][0])
                else:
                    if len(inp[0][0]) < 40:
                        if inp[0][3]:
                            inp[0][0] += event.unicode

    pygame.draw.rect(screen, inp[0][2], inp[0][1])

    text_surface = base_font.render(inp[0][0], True, (255, 255, 255))
    pygame.draw.rect(screen, (255, 0, 0), [430, 190, 210, 40])
    screen.blit(t, (460, 200))
    screen.blit(text_surface, (inp[0][1].x + 5, inp[0][1].y + 5))
    inp[0][1].w = max(500, text_surface.get_width() + 10)
    if len(mes_store) > 17:
        mes_store.pop(0)
    blit_text(screen, mes_store.copy(), (30, 270), base_font)

    if inp[0][3]:
        inp[0][2] = color_active
    else:
        inp[0][2] = color_passive

    try:
        while True:

            # Receive our "header" containing username length, it's size is defined and constant
            username_header = client_socket.recv(HEADER_LENGTH)

            # If we received no data, server gracefully closed a connection, for example using socket.close() or socket.shutdown(socket.SHUT_RDWR)
            if not len(username_header):
                print('Connection closed by the server')
                sys.exit()

            # Convert header to int value
            username_length = int(username_header.decode('utf-8').strip())

            # Receive and decode username
            username = client_socket.recv(username_length).decode('utf-8')

            # Now do the same for message (as we received username, we received whole message, there's no need to check if it has any length)
            message_header = client_socket.recv(HEADER_LENGTH)
            message_length = int(message_header.decode('utf-8').strip())
            message = client_socket.recv(message_length).decode('utf-8')

            # Print message
            print(f'{username} > {message}')
            mes_store.append(f'{username} > {message}')
            pygame.display.update()

    except IOError as e:
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            print('Reading error: {}'.format(str(e)))
            sys.exit()
        pygame.display.update()

        continue

    except Exception as e:
        print('Reading error: '.format(str(e)))
        sys.exit()

