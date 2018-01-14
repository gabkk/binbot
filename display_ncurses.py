import curses
import os


class Window():

    def __init__(self):
        # create stdscr
        stdscr = curses.initscr()
        stdscr.clear()

        # allow echo, set colors
        curses.echo()
        curses.curs_set(0)
        curses.start_color()
        curses.use_default_colors()
        rows, columns = os.popen('stty size', 'r').read().split()
        self.display_window = curses.newwin(10, int(columns), 0, 0)
        self.result_cmd_window = curses.newwin(3, int(columns), 10, 0)
        self.cmd_window = curses.newwin(3, int(columns), 13, 0)

        self.display_window.border()
        self.result_cmd_window.border()
        self.cmd_window.refresh()
        self.result_cmd_window.refresh()
        self.display_window.refresh()

    def my_raw_input(self, r, c, prompt_string):
        self.cmd_window.clear()
        self.cmd_window.border()
        self.cmd_window.addstr(r, c, prompt_string)
        self.cmd_window.refresh()
        input = self.cmd_window.getstr(r + 1, c + 1)
        return input

    def close_ncurses(self):
        curses.nocbreak()
        curses.endwin()

    def get_display_window(self):
        return self.display_window
