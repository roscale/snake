#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Rosca Alex 4TB
# snake.py – 23.03.16
# version 1.3.3 - Portabilité, résolu qqs bugs d'affichage

from os import system
import signal
from time import sleep
from random import randint
from multiprocessing import Process, Value, Manager
## Librairies téléchargées ##
import getch
from termcolor import colored, cprint


def affiche_grille(grille, largeur, longueur):
    global printed_pause
    global pause

    ###Bouge le curseur au dessus et affiche score ###
    cprint("\033[;H  Score: {}  ".format(score.value), 'white', 'on_cyan', ['bold'])
    # on utilise "\033[;H" pour remettre le curseur au dessus car la commande "clear" est trop lente
    # => overwrite

    ### Affichage matrice ###
    border = colored('+', 'yellow', 'on_yellow')
    print(border * (longueur * 2 + 4))
    for i in range(largeur):
        print(border * 2, end="")

        for j in range (longueur):
            print(grille[i][j], end=grille[i][j])
        print(border * 2)

    print(border * (longueur * 2 + 4))

    ## Si c'est finit ou pausé
    if game_over.value == True:
        print("Game Over")
        print("Réessayez ?[o/n]\n")

    if pause.value == True and printed_pause.value == False:
        print("Paused")
        printed_pause.value = True
    else:
        print("      ") ### Pour cacher le mot "Paused" => overwrite


def get_input():
    ### Prendre touche ###
    touche.value = ord(getch.getch())

    ## Flèches ##
    if touche.value == 27:
        touche.value = ord(getch.getch())
        if touche.value == 91:
            touche.value = ord(getch.getch())

    ## Pause ##
    if (touche.value == 32 or touche.value == 112) and game_over.value == False:
        if pause.value == False:
            pause.value = True
            printed_pause.value = False
        else:
            #system("clear")
            pause.value = False


    ## Réessayez ##
    if game_over.value == True:
        if touche.value == 111:
            reset()
        elif touche.value == 110:
            system('setterm -cursor on')
            exit()


def set_input():
    if pause.value == False and game_over.value == False:   ## Si il marche encore(pour ne pas tricher la direction)
        ### [z q s d] et flèches ###
        if (touche.value == 122 or touche.value == 65) and snake_direction.value != "down":
            snake_direction.value = "up"
        elif (touche.value == 115 or touche.value == 66) and snake_direction.value != "up":
            snake_direction.value = "down"
        elif (touche.value == 113 or touche.value == 68) and snake_direction.value != "right":
            snake_direction.value = "left"
        elif (touche.value == 100 or touche.value == 67) and snake_direction.value != "left":
            snake_direction.value = "right"


def check_position():
    ### Verifie si il se morde lui-même :P
    for snakeBlock in range(len(snake_list) - 3):
        if snake_list[-1] == snake_list[snakeBlock]:
            game_over.value = True
            return None

    ### Verifie si il est dans la grille(pas des valeurs negatives)
    if posLargSnake.value < 0 or posLargSnake.value >= largeur or posLongSnake.value < 0 or posLongSnake.value >= longueur:
        game_over.value = True
        return None


def update_snake():
    ### Modifie les coordonés ###
    if snake_direction.value == "up":
        posLargSnake.value -= 1
    elif snake_direction.value == "down":
        posLargSnake.value += 1
    elif snake_direction.value == "left":
        posLongSnake.value -= 1
    elif snake_direction.value == "right":
        posLongSnake.value += 1

    check_position()    ## Verifie si la position est corècte

    if game_over.value == True:     ## Bravo, T'AS PERDU
        return None

    ### Efface ###
    for snake_block in snake_list:
        grille[snake_block[0]][snake_block[1]] = colored_space.value

    ### Actualise les valeurs ###
    snake_head = []
    snake_head.append(posLargSnake.value)
    snake_head.append(posLongSnake.value)
    snake_list.append(snake_head)

    if len(snake_list) > snake_blocks.value:
        snake_list.pop(0)

    ### Actualise la grille ###
    for snake_block in snake_list:
        if snake_block == snake_head:
            grille[snake_block[0]][snake_block[1]] = colored_snake_head.value
        else:
            grille[snake_block[0]][snake_block[1]] = colored_snake_body.value


def check_point_eaten():
    if snake_list[-1] == point_pos:     ## Si le point est mangé
        spawn_point()
        snake_blocks.value += 1
        score.value += 1
        game_speed.value -= 0.0025


def spawn_point():
    global point_pos

    x = randint(0, largeur - 1)
    y = randint(0, longueur - 1)

    while grille[x][y] == colored_snake_body.value or grille[x][y] == colored_snake_head.value:      ### Au cas ou, si le point est dans le snake il se regénère
        x = randint(0, largeur - 1)
        y = randint(0, longueur - 1)

    point_pos = []
    point_pos.append(x)
    point_pos.append(y)

    grille[x][y] = colored_point.value


def timer_snake():
    while True:
        if pause.value == False and game_over.value == False:   # Tant que tout va bien
            set_input()                 #
            update_snake()              #   Le coeur du jeu
            check_point_eaten()         #

            ### Affichage de la grille ###
            affiche_grille(grille, largeur, longueur)

            ### Attend avant de réappeler la fonction(vitesse de jeu) ###
            try:
                sleep(game_speed.value)
            except:
                game_speed.value = 0
                ### Le + vite possible, pas de valeur négative


        elif pause.value == True:
            if printed_pause.value == False:
                affiche_grille(grille, largeur, longueur)
            sleep(0.1) ### Pour ne pas stresser le processeur dans la boucle while

        elif game_over.value == True:
            return None


def reset():
    global grille
    global processus

    processus.terminate()

    grille = [[colored_space.value for y in range(longueur)] for x in range(largeur)]
    snake_list = []
    snake_direction.value = "right"
    snake_blocks.value = 2
    posLargSnake.value = 1
    posLongSnake.value = 1
    snake_head = []
    point_pos = []
    score.value = 0
    game_over.value = False
    pause.value = False
    printed_pause.value = True
    game_speed.value = game_speed_org

    spawn_point()

    system("clear")
    processus = Process(target=timer_snake)
    processus.start()


def quit(signal, frame):
    print()
    system('setterm -cursor on') # Réafficher le curseur si on fait CTRL+C
    exit(0)



snake_list = []
snake_direction = Manager().Value('ctypes.c_char_p', "right")   ## Variable partagée avec l'autre processus
snake_blocks = Manager().Value('i', 2)
game_speed = Manager().Value('f', .5)

posLargSnake = Manager().Value('i', 1)
posLongSnake = Manager().Value('i', 1)

snake_head = Manager().list()
snake_head.append(1)
snake_head.append(2)

point_pos = Manager().list()
score = Manager().Value('i', 0)
game_over = Manager().Value('b', False)
pause = Manager().Value('b', False)
printed_pause = Manager().Value('b', True)
touche = Manager().Value('i', 0)

colored_space = Manager().Value('ctypes.c_char_p', colored(' ', 'grey', 'on_grey'))
colored_snake_body = Manager().Value('ctypes.c_char_p', colored('x', 'green', 'on_green'))
colored_snake_head = Manager().Value('ctypes.c_char_p', colored('x', 'white', 'on_white'))
colored_point = Manager().Value('ctypes.c_char_p', colored('o', 'red', 'on_red'))

signal.signal(signal.SIGINT, quit)

### Programme principal ###
system('clear')

print("Les touches de mouvement sont les flèches ou [z q s d].")
print("La touche de pause est l'éspace ou [p].\n")

longueur = int(input("Longueur de la grille: "))
largeur = int(input("Largeur de la grille: "))
grille = [[colored_space.value for y in range(longueur)] for x in range(largeur)]

game_speed.value = (6 - float(input("Vitesse de départ[0-5]: "))) / 10
game_speed_org = game_speed.value   ## Garder la valeur pour réessaye

spawn_point()
system("clear")
system('setterm -cursor off')

### Processus ###
processus = Process(target=timer_snake)
processus.start()

while True:
    get_input()
