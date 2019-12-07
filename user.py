import pygame
import socket
import sys
import threading
import os

# Arquivos criados
from grid import Grid
########### VARIAVEIS GLOBAIS ###########

# tela
os.environ['SDL_VIDEO_WINDOW_POS'] = '200,100'
surface = pygame.display.set_mode((600, 600))
pygame.display.set_caption('Tic-tac-toe')

# Endereço para conexão
ip = '127.0.0.1'
port = 65432

# Estanciamento do socket
sock = None
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Auxiliares de conexão
conn = None
addr = None

# Variaveis do jogo
running = True
turn = False
table = []
lider = False
pos_turn = False
ok_move = True

# Inicialização dos objetos
grid = Grid()


def create_thread(target, connect):
        thread = threading.Thread(target=target, args=(connect,))
        thread.daemon = True
        thread.start()

def createRoom():
        global sock, ip, port
        try:
                sock.bind((ip, port))
                sock.listen(10)
                print('\n ***Você é o Player 1***')
                return sock
        except Exception as e:
                print(e)
                return False

def connectToRoom():
        global ip, port, sock
        try:
                sock.connect((ip, port))
                print('\n ***Você é o Player 2***')
                return sock
        except:
                print('\nNão consegui conexão. Verifique sua rede.')
                return False

def waiting_for_connection():
        global conn, addr
        print('\nAguardando conexão do Player 2.')
        conn, addr = sock.accept()
        print(addr, 'se conectou. Bem vindo!')
        playing = True
        return conn

def accord(connect, player):
        global table, ok_move
        print('\nVocê solicitou aprovação para ser o lider.')
        send_data = '{}-{}-{}-{}'.format('requisição', '#### Player', player,'fez solicitação para ser lider.').encode()
        connect.send(send_data)

        if len(table) > 0 and ok_move:
                if table[len(table)-1] != player:
                        print('\n-- Você é o lider agora. --')
                        send_data = '{}-{}-{}-{}'.format('requisição', '\nPlayer', player, 'se tornou lider.').encode()
                        connect.send(send_data)
                        return True
        else:
                print('\nPedido de liderança rejeitado.')
                return False

def receive_data(connect):
        global turn, table, ok_move
        you_is = 0
        while True:
                data = connect.recv(1024).decode() # receive data
                data = data.split('-') # the format of the data after splitting is: (cellX, cellY, playing, player)
                if data[0] == 'requisição':
                        print(data[1], data[2], data[3])
                elif data[0] == 'invalido':
                        turn = True
                else:
                        x, y = int(data[0]), int(data[1])
                        if data[2] == 'False' or grid.is_grid_full():
                                if grid.is_grid_full():
                                        print('\nHouve um empate!!')
                                else:
                                        print('Você perdeu. :(')
                                send_data = '{}'.format('invalido').encode()
                                connect.send(send_data)
                                grid.game_over = True
                                table = []
                        elif data[3] == 'X':
                                you_is = 2
                                if grid.get_cell_value(x, y) == 0:
                                        grid.set_cell_value(x, y, 'X')
                                        ok_move = True
                                        table.append(data[3])
                                        print('\n>>> Sequencia de jogadas:', table)
                                else:
                                        ok_move = False
                                        send_data = '{}-{}-{}-{}'.format('requisição', 'Jogada', '', 'invalida.').encode()
                                        connect.send(send_data)
                        elif data[3] == 'O':
                                you_is = 1
                                if grid.get_cell_value(x, y) == 0:
                                        grid.set_cell_value(x, y, 'O')
                                        ok_move = True
                                        table.append(data[3])
                                        print('\n>>> Sequencia de jogadas:', table)
                                else:
                                        ok_move = False
                                        send_data = '{}-{}-{}-{}'.format('requisição', 'Jogada', '', 'invalida.').encode()
                                        connect.send(send_data)
                        if data[5] != []:
                                print('>>>> Jogadas', table)
                        if data[4] == 'youturn':
                                if accord(connect, you_is):
                                        turn = True
                                else:
                                        send_data = '{}'.format('invalido').encode()
                                        connect.send(send_data)

def main():
        global grid, running, lider, turn
        fx = True
        room = createRoom()

        if room == False:
                user = connectToRoom()
                if user == False:
                        print('\nNão consegui se conectar em uma sala. Verifique sua rede.')
                else:
                        # >>>>>>>>>>>>>> PLAYER 2
                        create_thread(receive_data, user)
                        player = "O"
                        playing = 'True'
                        # LOOP PLAYER 2
                        while running:
                                for event in pygame.event.get():
                                        if event.type == pygame.QUIT:
                                                running = False
                                        if event.type == pygame.MOUSEBUTTONDOWN and not grid.game_over:
                                                if pygame.mouse.get_pressed()[0]:
                                                        if turn and not grid.game_over:
                                                                pos = pygame.mouse.get_pos()
                                                                cellX, cellY = pos[0] // 200, pos[1] // 200
                                                                grid.get_mouse(cellX, cellY, player)
                                                                if grid.game_over:
                                                                        playing = 'False'
                                                                table.append(player)
                                                                send_data = '{}-{}-{}-{}-{}-{}'.format(cellX, cellY, playing, player, 'youturn',table).encode()
                                                                user.send(send_data)
                                                                turn = False
                                surface.fill((0,0,0))
                                grid.draw(surface)
                                pygame.display.flip()
        # >>>>>>>>>>>>>> FIM DO PLAYER 2
        else:
                # >>>>>>>>>>>>>> PLAYER 1
                connec = waiting_for_connection()
                create_thread(receive_data, connec)
                player = "X"
                turn = True
                lider = True
                playing = 'True'
                # LOOP PLAYER 1
                while running:
                        for event in pygame.event.get():
                                if event.type == pygame.QUIT:
                                        running = False
                                if event.type == pygame.MOUSEBUTTONDOWN and fx:
                                        if pygame.mouse.get_pressed()[0]:
                                                if turn and not grid.game_over:
                                                        pos = pygame.mouse.get_pos()
                                                        cellX, cellY = pos[0] // 200, pos[1] // 200
                                                        grid.get_mouse(cellX, cellY, player)
                                                        if grid.game_over:
                                                                playing = 'False'
                                                        table.append(player)
                                                        send_data = '{}-{}-{}-{}-{}-{}'.format(cellX, cellY, playing, player,'youturn',table).encode()
                                                        connec.send(send_data)
                                                        turn = False
                        surface.fill((0,0,0))
                        grid.draw(surface)
                        pygame.display.flip()
                # >>>>>>>>>>>>>> FIM DO PLAYER 1


if __name__ == "__main__":
    main()
