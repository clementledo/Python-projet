import curses
import time
import pygame
import logging
import sys
from contextlib import contextmanager
import webbrowser

class CursesView:
    def __init__(self, game_map, game=None, running_server=False, port=8000):
        self.game = game
        self.running_server = running_server
        self.port = port
        # Setup logging to file instead of stdout
        logging.basicConfig(filename='game_debug.log', 
                          level=logging.DEBUG,
                          format='%(asctime)s - %(levelname)s - %(message)s')
        
        # Store original stdout
        self.old_stdout = sys.stdout
        # Redirect stdout to log file
        sys.stdout = open('game_output.log', 'a')
        
        self.map = game_map
        
        
        # Hide Pygame window
        pygame.display.iconify()
        
        self.screen = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self.screen.keypad(True)
        self.screen.nodelay(True)  # Non-blocking input
        curses.curs_set(0)
        curses.start_color()
        curses.init_pair(1, curses.COLOR_BLUE, curses.COLOR_BLACK)    # Player 1
        curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)     # Player 2
        curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # Resources
        curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)   # Empty

        self.color_pairs = {
            'player1': curses.color_pair(1),
            'player2': curses.color_pair(2),
            'resource': curses.color_pair(3),
            'empty': curses.color_pair(4)
        }

        self.offset_x = 0
        self.offset_y = 0
        self.scroll_speed = 2
        self.fast_scroll_speed = 3
        self.paused = False

        try:
            self.run_display()
        finally:
            self.cleanup()

    def cleanup(self):
        if self.screen:
            self.screen.keypad(False)
            curses.echo()
            curses.nocbreak()
            curses.endwin()
            
        # Restore original stdout
        sys.stdout.close()
        sys.stdout = self.old_stdout
        
        # Restore Pygame window
        pygame.init
        pygame.display.flip()

    def run_display(self):
        while True:
            if not self.paused:
                self.screen.erase()
                self.draw_map()
                self.screen.noutrefresh()
                curses.doupdate()

            time.sleep(0.01)

            # Handle keyboard input
            key = self.screen.getch()
            if key == ord('p'):
                self.paused = not self.paused
            elif key == 27:  # ESC
                return True
            elif key == ord('\t'):  # TAB key
                if self.game:
                    # Write to game_data.json in current directory
                    with open('game_data.json', 'w') as f:
                        f.write(self.game.to_json())
                    if self.running_server:
                        # Force refresh browser tab
                        webbrowser.open_new(f"http://localhost:{self.port}/game_data.json")
            elif key == curses.KEY_F9:
                return True

            # Handle scrolling
            if not self.paused:
                # ZQSD keys
                if key == ord('z'):
                    self.offset_y -= self.scroll_speed
                elif key == ord('s'):
                    self.offset_y += self.scroll_speed
                elif key == ord('q'):
                    self.offset_x -= self.scroll_speed
                elif key == ord('d'):
                    self.offset_x += self.scroll_speed
                # Arrow keys
                elif key == curses.KEY_UP:
                    self.offset_y -= self.scroll_speed
                elif key == curses.KEY_DOWN:
                    self.offset_y += self.scroll_speed
                elif key == curses.KEY_LEFT:
                    self.offset_x -= self.scroll_speed
                elif key == curses.KEY_RIGHT:
                    self.offset_x += self.scroll_speed
                # Shift modifier for fast scrolling
                elif key == ord('Z'):
                    self.offset_y -= self.fast_scroll_speed
                elif key == ord('S'):
                    self.offset_y += self.fast_scroll_speed
                elif key == ord('Q'):
                    self.offset_x -= self.fast_scroll_speed
                elif key == ord('D'):
                    self.offset_x += self.fast_scroll_speed

                # Keep offset within bounds
                self.offset_x = max(0, min(self.offset_x, self.map.width - self.screen.getmaxyx()[1]))
                self.offset_y = max(0, min(self.offset_y, self.map.height - self.screen.getmaxyx()[0]))

    def draw_map(self):
        height, width = self.screen.getmaxyx()
        max_y = min(self.map.height - self.offset_y, height)
        max_x = min(self.map.width - self.offset_x, width // 2)

        for screen_y in range(max_y):
            for screen_x in range(max_x):
                # Calculer les coordonnées réelles sur la map en tenant compte des offsets
                map_y = screen_y + self.offset_y
                map_x = screen_x + self.offset_x
                
                if 0 <= map_y < self.map.height and 0 <= map_x < self.map.width:
                    tile = self.map.grid[map_y][map_x]
                    if tile.occupant:
                        if isinstance(tile.occupant, list):
                            unit = tile.occupant[0]
                            color = self.color_pairs['player1'] if unit.player_id == 1 else self.color_pairs['player2']
                            self.screen.addch(screen_y, screen_x*2, unit.symbol, color)
                        else:
                            entity = tile.occupant
                            color = self.color_pairs['player1'] if entity.player_id == 1 else self.color_pairs['player2']
                            self.screen.addch(screen_y, screen_x*2, entity.symbol, color)
                    elif tile.has_resource():
                        self.screen.addch(screen_y, screen_x*2, tile.resource.type.value, self.color_pairs['resource'])
                    else:
                        self.screen.addch(screen_y, screen_x*2, '.', self.color_pairs['empty'])