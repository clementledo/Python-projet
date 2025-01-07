import pygame
import pickle

def main_menu(screen, game_state):
    """
    Affiche le menu principal.
    Retourne une action basée sur l'entrée utilisateur.
    """
    bg_image = pygame.image.load("assets/bg_Menu.png").convert()
    font = pygame.font.SysFont("Arial", 36)

    buttons = [
        {"label": "Start Game", "action": "start", "rect": pygame.Rect(670, 820, 200, 50)},
        {"label": "Load Game", "action": "load", "rect": pygame.Rect(890, 820, 200, 50)},
        {"label": "Quit", "action": "quit", "rect": pygame.Rect(1110, 820, 200, 50)},
    ]

    running = True
    while running:
        screen.blit(bg_image, (0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Clic gauche
                for button in buttons:
                    if button["rect"].collidepoint(event.pos):
                        print(f"Button clicked: {button['label']}")  # Debug message
                        if button["action"] == "load":
                            game_state.load_state()  # Utilise GameState pour charger
                        return button["action"]

        for button in buttons:
            pygame.draw.rect(screen, (90, 42, 42), button["rect"])
            text = font.render(button["label"], True, (255, 255, 255))
            screen.blit(
                text,
                (
                    button["rect"].x + (button["rect"].width - text.get_width()) // 2,
                    button["rect"].y + (button["rect"].height - text.get_height()) // 2,
                ),
            )

        pygame.display.flip()

    return "quit"

def pause_menu(screen, game_state):
    """
    Affiche le menu de pause.
    Retourne une action basée sur l'entrée utilisateur.
    """
    # Charger l'image d'arrière-plan (optionnelle)
    bg_image = pygame.image.load("assets/bg_Menu2.png").convert()
    bg_color = (0, 0, 0.5)  # Fond noir semi-transparent
    font = pygame.font.SysFont("Arial", 36)

    # Définir les boutons
    buttons = [
        {"label": "Resume", "action": "resume", "rect": pygame.Rect(412, 250, 200, 50)},
        {"label": "Save Game", "action": "save", "rect": pygame.Rect(412, 320, 200, 50)},
        {"label": "Load Game", "action": "load", "rect": pygame.Rect(412, 390, 200, 50)},
        {"label": "Main Menu", "action": "main_menu", "rect": pygame.Rect(412, 460, 200, 50)},
        {"label": "Quit", "action": "quit", "rect": pygame.Rect(412, 530, 200, 50)},
    ]

    running = True
    while running:
        # Rendre le fond semi-transparent
        screen.blit(bg_image,(0,0))
        overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        #overlay.fill((0, 0, 0.5, 10))  # Semi-transparent noir
        screen.blit(overlay, (0, 0))

        # Gérer les événements
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Clic gauche
                for button in buttons:
                    if button["rect"].collidepoint(event.pos):
                        print(f"Button clicked: {button['label']}")
                        return button["action"]  

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Clic gauche
                for button in buttons:
                    if button["rect"].collidepoint(event.pos):
                        if button["action"] == "save":
                            game_state.save_state("save_game.pkl")  # Sauvegarde
                        elif button["action"] == "load":
                            game_state.load_state("save_game.pkl")  # Chargement
                        return button["action"]

        # Dessiner les boutons
        for button in buttons:
            pygame.draw.rect(screen, (90, 42, 42), button["rect"])
            text = font.render(button["label"], True, (255, 255, 255))
            screen.blit(
                text,
                (
                    button["rect"].x + (button["rect"].width - text.get_width()) // 2,
                    button["rect"].y + (button["rect"].height - text.get_height()) // 2,
                ),
            )

        pygame.display.flip()

    return "quit"


