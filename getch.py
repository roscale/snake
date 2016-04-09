import sys, tty, termios

def getch():
    old_settings = termios.tcgetattr(sys.stdin.fileno())
    try:
        tty.setcbreak(sys.stdin.fileno())
        c = sys.stdin.read(1)
        return(c)
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
