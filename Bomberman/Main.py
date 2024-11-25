import g2d, time
import pygame as pg
from GameBomberman import main as start_game
from GameSettings import GameSettings

SEC_MULTIPLIER = 0.7
DIST = 0  # Distance of GUI from borders


class GameMenu:
    def __init__(self):
        # Crea un'istanza delle impostazioni del gioco
        self.settings = GameSettings()
        self.in_settings = False
        self.selected_option = "START"  # Options: "START" or "SETTINGS"
        self.last_switch_time = time.time() * 1000 / SEC_MULTIPLIER
        self.show_alternate = False
        self.show_message = None  # Messaggio temporaneo da mostrare
        self.message_time = 0  # Tempo di inizio del messaggio

        self.images = {
            "START": "GUIs/BombermanTitleStart.png",
            "SETTINGS": "GUIs/BombermanTitleSettings.png",
            "EMPTY": "GUIs/BombermanTitleEmpty.png"
        }

        # Initialize pygame mixer for music
        pg.mixer.init()
        self.music_playing = False

    def tick(self):
        g2d.clear_canvas()
        g2d.set_color((0, 0, 0))
        g2d.draw_rect((0, 0), (g2d.canvas_size()))
        self.handle_navigation()
        self.draw_menu()
        self.draw_message()
        g2d.update_canvas()

        # Play menu music in loop if not already playing
        if not self.music_playing and not self.settings.MUTE_MUSIC:
            self.play_music()

    def handle_navigation(self):
        current_time = time.time() * 1000 / SEC_MULTIPLIER  # Current time in milliseconds
        if current_time - self.last_switch_time >= 1000:  # Switch every second
            self.show_alternate = not self.show_alternate
            self.last_switch_time = current_time

        if g2d.key_pressed("ArrowRight"):
            self.selected_option = "SETTINGS"
        elif g2d.key_pressed("ArrowLeft"):
            self.selected_option = "START"

        if g2d.key_pressed("Enter"):
            if self.selected_option == "START":
                self.start_game()
            elif self.selected_option == "SETTINGS":
                #self.in_settings = True
                self.show_message = "Settings are work in progress (edit GameSettings.py)"
                self.message_time = current_time

    def draw_menu(self):
        # Alternate the visible image based on the state
        image_to_draw = self.images["EMPTY"] if self.show_alternate else self.images[self.selected_option]
        
        # Resize the image to fit the canvas
        self.draw_resized_image(image_to_draw, (0, 0))

        if self.in_settings:
            self.draw_settings()

    def draw_message(self):
        if self.show_message:
            current_time = time.time() * 1000 / SEC_MULTIPLIER
            # Mostra il messaggio per 2 secondi
            if current_time - self.message_time < 7000:
                g2d.set_color((0, 0, 0))
                g2d.draw_rect((0, 0), (g2d.canvas_size()))
                g2d.set_color((255, 255, 255))
                g2d.draw_text(self.show_message, (g2d.canvas_size()[0]/2,g2d.canvas_size()[1]/2), 11)
            else:
                self.show_message = None  # Nascondi il messaggio dopo 2 secondi

    def draw_settings(self):
        pass

    def start_game(self):
        pg.mixer.music.stop()
        
        if not self.settings.MUTE_MUSIC:
            self.play_level_music()
        
        # Passa l'istanza di GameSettings a GameBomberman
        start_game(self.settings)

    def play_music(self):
        # Load and play the main menu music in a loop
        music_path = "Soundtracks/mainMenu.mp3"
        pg.mixer.music.load(music_path)
        pg.mixer.music.set_volume(self.settings.VOLUME)
        pg.mixer.music.play(-1)  # -1 means loop forever
        self.music_playing = True
        
    def stop_all_sounds(self):
        """Ferma tutta la musica e gli effetti sonori in riproduzione."""
        pg.mixer.music.stop()  # Ferma la musica
        pg.mixer.stop()  # Ferma tutti i canali audio
        pg.mixer.fadeout(500)  # Sfumatura finale (opzionale)

    def play_level_music(self):
        self.stop_all_sounds()
        pg.mixer.music.load("Soundtracks/levelTheme.mp3")
        pg.mixer.music.set_volume(self.settings.VOLUME)

        pg.mixer.music.play(-1)  # -1 means that music is looping
    
    def draw_resized_image(self, image_path, position):
        # Get the dimensions of the canvas
        canvas_width, canvas_height = g2d.canvas_size()
        
        # Load the image
        image = g2d.load_image(image_path)
        
        # Get the original dimensions of the image
        image_surface = g2d._loaded[image]  # Directly access the loaded images dictionary
        original_width, original_height = image_surface.get_size()

        # Calculate the scale factor to maintain proportions
        width_ratio = (canvas_width - 2 * DIST) / original_width  # Consider the distance from the borders
        height_ratio = (canvas_height - 2 * DIST) / original_height  # Consider the distance from the borders
        scale_factor = min(width_ratio, height_ratio)  # Maintain the proportion

        # New dimensions
        new_width = int(original_width * scale_factor)
        new_height = int(original_height * scale_factor)

        # Resize the image
        resized_image = pg.transform.scale(image_surface, (new_width, new_height))
        
        # Calculate the position to center the image, considering the distance from borders
        center_x = max(DIST, (canvas_width - new_width) // 2)  # Ensure the image is not too close to the border
        center_y = max(DIST, (canvas_height - new_height) // 2)  # Ensure the image is not too close to the border

        # Draw the resized image centered with a distance from the border
        g2d._canvas.blit(resized_image, (center_x, center_y))


def main():
    g2d.init_canvas((256, 240), scale=3)
    menu = GameMenu()
    g2d.main_loop(menu.tick)

if __name__ == "__main__":
    main()
