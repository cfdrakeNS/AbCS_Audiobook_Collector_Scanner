import curses
import traceback

def draw_terminal(stdscr):
    try:
        # Clear screen and turn off cursor blinking
        stdscr.clear()
        curses.curs_set(0)
        
        # Write a simple test line first
        stdscr.addstr(0, 0, "SIMULATOR ACTIVE - PRESS ANY KEY TO EXIT", curses.A_REVERSE)
        stdscr.addstr(2, 0, "If you see this, the buffer is working for JAWS.")
        
        stdscr.refresh()
        stdscr.getch() # This IS the wait command
    except Exception:
        # If it crashes, this keeps the error on screen
        stdscr.clear()
        stdscr.addstr(0, 0, "ERROR ENCOUNTERED:")
        stdscr.addstr(2, 0, traceback.format_exc()[:400])
        stdscr.refresh()
        stdscr.getch()

if __name__ == "__main__":
    curses.wrapper(draw_terminal)