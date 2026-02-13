import pygame
import os
import settings

# ASSET MANAGER

class AssetManager:
    def __init__(self):
        self.original_images = {}
        self.scaled_images = {}
        self.sounds = {}
        self.placeholder_font = None

    def load_content(self):
        # sounds
        sound_files = {'move': 'move.ogg', 'capture': 'capture.ogg'}
        for name, filename in sound_files.items():
            path = os.path.join(settings.SOUND_DIR, filename)
            if os.path.exists(path):
                self.sounds[name] = pygame.mixer.Sound(path)

        # images
        pieces = ['wp', 'wr', 'wn', 'wb', 'wq', 'wk', 'bp', 'br', 'bn', 'bb', 'bq', 'bk']
        for filename in pieces:
            # key example: 'P' for white pawn, 'p' for black pawn
            key = filename[1].upper() if filename.startswith('w') else filename[1]
            path = os.path.join(settings.IMAGE_DIR, f"{filename}.png")
            if os.path.exists(path):
                self.original_images[key] = pygame.image.load(path)
            else:
                self.original_images[key] = None

    def rescale_images(self, sq_size):
        self.scaled_images.clear()
        
        # font for placeholders
        self.placeholder_font = pygame.font.SysFont("Arial", int(sq_size * 0.4), bold=True)

        for key, img in self.original_images.items():
            if img:
                self.scaled_images[key] = pygame.transform.smoothscale(img, (sq_size, sq_size))
            else:
                # generate text placeholder
                s = pygame.Surface((sq_size, sq_size), pygame.SRCALPHA)
                color = settings.BLACK if key.islower() else settings.WHITE
                text = self.placeholder_font.render(key, True, color)
                rect = text.get_rect(center=(sq_size//2, sq_size//2))
                s.blit(text, rect)
                self.scaled_images[key] = s

    def get_image(self, piece_symbol):
        return self.scaled_images.get(piece_symbol)

    def play_sound(self, name):
        if name in self.sounds:
            self.sounds[name].play()