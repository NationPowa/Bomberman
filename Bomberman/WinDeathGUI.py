import g2d
import time
import pygame as pg
from GameSettings import GameSettings

SEC_MULTIPLIER = 0.7
DIST = 0  # Distance of GUI from borders

class WinDeathGUI:
    def __init__(self, outcome):
        self.outcome = outcome  # "WIN" o "DEATH"
        self.settings = GameSettings()
        self.last_switch_time = time.time() * 1000 / SEC_MULTIPLIER
        self.show_alternate = False

        # Carica le immagini per la GUI
        self.images = {
            "WIN": "GUIs/BombermanWin.png",
            "DEATH": "GUIs/BombermanDeath.png",
            "EMPTY_WIN": "GUIs/BombermanWinEmpty.png",
            "EMPTY_DEATH": "GUIs/BombermanDeathEmpty.png"
        }

        # Inizializza la musica
        pg.mixer.init()
        self.win_sound = pg.mixer.Sound("Soundtracks/levelCompleted.mp3")
        self.death_sound = pg.mixer.Sound("Soundtracks/death.mp3")
        self.win_sound.set_volume(self.settings.VOLUME)
        self.death_sound.set_volume(self.settings.VOLUME)

        # Riproduci la musica dell'outcome (se non muto)
        self.play_outcome_music()

    def play_outcome_music(self):
        """Riproduce la musica in base al risultato."""
        pg.mixer.stop()  # Ferma qualsiasi musica precedente
        if not self.settings.MUTE_MUSIC:
            self.stop_all_sounds()
            if self.outcome == "WIN":
                self.win_sound.play()
            elif self.outcome == "DEATH":
                self.death_sound.play()

    def tick(self):
        """Main loop: gestisce la logica del gioco e l'input."""
        g2d.clear_canvas()
        self.handle_input()
        self.draw_outcome()
        g2d.update_canvas()

    def handle_input(self):
        """Gestisce l'input dell'utente (es. premere 'Enter' per riprendere il gioco)."""
        current_time = time.time() * 1000 / SEC_MULTIPLIER  # Tempo corrente in millisecondi
        if current_time - self.last_switch_time >= 1000:  # Cambia l'immagine ogni secondo
            self.show_alternate = not self.show_alternate
            self.last_switch_time = current_time

        if g2d.key_pressed("Enter"):
            self.restart_game()

    def draw_outcome(self):
        """Disegna l'outcome (vittoria o morte) sulla GUI."""
        if self.outcome == "WIN":
            image_to_draw = self.images["EMPTY_WIN"] if self.show_alternate else self.images["WIN"]
        elif self.outcome == "DEATH":
            image_to_draw = self.images["EMPTY_DEATH"] if self.show_alternate else self.images["DEATH"]
        else:
            return

        self.draw_resized_image(image_to_draw, (0, 0))

    def restart_game(self):
        """Riavvia il gioco."""
        from GameBomberman import main as start_game
        pg.mixer.music.stop()  # Ferma la musica

        # Se non è muto, riprendi la musica del livello
        if not self.settings.MUTE_MUSIC:
            self.play_level_music()
        
        # Passa l'istanza di GameSettings a GameBomberman
        start_game(self.settings)

    def play_level_music(self):
        """Riproduce la musica del livello."""
        self.stop_all_sounds()
        pg.mixer.music.load("Soundtracks/levelTheme.mp3")
        pg.mixer.music.set_volume(self.settings.VOLUME)
        pg.mixer.music.play(-1)  # -1 significa che la musica è in loop
    
    def stop_all_sounds(self):
        """Ferma tutta la musica e gli effetti sonori in riproduzione."""
        pg.mixer.music.stop()  # Ferma la musica
        pg.mixer.stop()  # Ferma tutti i canali audio
        pg.mixer.fadeout(500)  # Sfumatura finale (opzionale)

    def draw_resized_image(self, image_path, position):
        """Disegna un'immagine ridimensionata per adattarla alla tela."""
        # Ottieni le dimensioni della tela
        canvas_width, canvas_height = g2d.canvas_size()
        
        # Carica l'immagine
        image = g2d.load_image(image_path)
        
        # Ottieni le dimensioni originali dell'immagine
        image_surface = g2d._loaded[image]
        original_width, original_height = image_surface.get_size()

        # Calcola il fattore di scala per mantenere le proporzioni
        width_ratio = (canvas_width - 2 * DIST) / original_width
        height_ratio = (canvas_height - 2 * DIST) / original_height
        scale_factor = min(width_ratio, height_ratio)

        # Nuove dimensioni
        new_width = int(original_width * scale_factor)
        new_height = int(original_height * scale_factor)

        # Ridimensiona l'immagine
        resized_image = pg.transform.scale(image_surface, (new_width, new_height))
        
        # Centra l'immagine
        center_x = max(DIST, (canvas_width - new_width) // 2)
        center_y = max(DIST, (canvas_height - new_height) // 2)

        # Disegna l'immagine ridimensionata
        g2d._canvas.blit(resized_image, (center_x, center_y))

def main(outcome):
    """Funzione principale che inizializza la GUI di vittoria o morte."""
    g2d.init_canvas((256, 240), scale=3)
    gui = WinDeathGUI(outcome)
    g2d.main_loop(gui.tick)
