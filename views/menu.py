import pygame
import pickle

def main_menu(screen, game_state):
    """
    Affiche le menu principal.
    Retourne une action basée sur l'entrée utilisateur.
    """
    bg_image = pygame.image.load("assets/bg_Menu.png").convert()
    font = pygame.font.SysFont("Cinzel", 48)

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
                        if button["action"] == "start":
                            settings_result = settings_menu(screen)
                            return settings_result  # Return settings result directly to main.py
                        elif button["action"] == "load":
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
    font = pygame.font.SysFont("Cinzel", 48)

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

def settings_menu(screen):
    bg_image = pygame.image.load("assets/parametre.gif").convert()
    
    # Use Cinzel font for medieval/strategy game feel
    font_main_title = pygame.font.SysFont("Cinzel", 80, bold=True)  # Large title
    font_title = pygame.font.SysFont("Cinzel", 60, bold=True)      # Section headers
    font = pygame.font.SysFont("Cinzel", 48)                       # Regular text

    # Alternative fonts if Cinzel is not available
    try:
        font_main_title = pygame.font.Font("assets/fonts/Cinzel-Bold.ttf", 72)
        font_title = pygame.font.Font("assets/fonts/Cinzel-Bold.ttf", 48)
        font = pygame.font.Font("assets/fonts/Cinzel-Regular.ttf", 36)
    except:
        print("Fallback to system fonts")
    
    # Screen dimensions
    SCREEN_WIDTH = screen.get_width()
    SCREEN_HEIGHT = screen.get_height()

    # Settings sections
    SECTION_MARGIN = 100
    BUTTON_SPACING = 70

    map_sizes = ["Small", "Medium", "Large"]
    map_types = ["centre_ressources", "ressources_generales"]
    selected_size = 1
    selected_type = 0

    starting_conditions = ["Maigre", "Moyenne", "Marines"]
    selected_condition = 1

    # Main buttons
    buttons = [
        {"label": "Start", "action": "start_game", "rect": pygame.Rect(670, 1020, 200, 50)},
        {"label": "Back", "action": "back", "rect": pygame.Rect(890, 1020, 200, 50)}
    ]

    # Map size section - Moved down
    size_buttons = [
        {"label": size, "rect": pygame.Rect(600, 530 + i*BUTTON_SPACING, 200, 50)} 
        for i, size in enumerate(map_sizes)
    ]

    # Map type section - Moved down with more spacing
    type_buttons = [
        {"label": "                    "+type_name, "rect": pygame.Rect(530, 800 + i*BUTTON_SPACING, 380, 50)}
        for i, type_name in enumerate(map_types)
    ]

    condition_buttons = [
        {"label": cond, "rect": pygame.Rect(1300, 430 + i*BUTTON_SPACING, 200, 50)}
        for i, cond in enumerate(starting_conditions)
    ]

    running = True
    while running:
        screen.blit(bg_image, (0, 0))

        # Draw main title
        main_title = font_main_title.render("SETTINGS", True, (90, 42, 42))  # Dark brown
        title_rect = main_title.get_rect(center=(SCREEN_WIDTH//2+30, 197))
        screen.blit(main_title, title_rect)

        # Draw section titles
        title_size = font_title.render("Map Size", True, (90, 42, 42))
        title_type = font_title.render("Resource Distribution", True, (90, 42, 42))
        title_condition = font_title.render("Starting Condition", True, (90, 42, 42))
        screen.blit(title_size, (600, 460))
        screen.blit(title_type, (500, 730))
        screen.blit(title_condition, (1250, 350))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return {"action": "quit"}

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for button in buttons:
                    if button["rect"].collidepoint(event.pos):
                        if button["action"] == "start_game":
                            return {
                                "action": "start",
                                "map_size": map_sizes[selected_size],
                                "map_type": map_types[selected_type],
                                "starting_condition": starting_conditions[selected_condition]
                            }
                        elif button["action"] == "back":
                            return "back"

                for i, size_button in enumerate(size_buttons):
                    if size_button["rect"].collidepoint(event.pos):
                        selected_size = i

                for i, type_button in enumerate(type_buttons):
                    if type_button["rect"].collidepoint(event.pos):
                        selected_type = i

                for i, condition_button in enumerate(condition_buttons):
                    if condition_button["rect"].collidepoint(event.pos):
                        selected_condition = i

        # Draw main buttons
        for button in buttons:
            pygame.draw.rect(screen, (90, 42, 42), button["rect"])
            text = font.render(button["label"], True, (255, 255, 255))
            screen.blit(text, (
                button["rect"].x + (button["rect"].width - text.get_width()) // 2,
                button["rect"].y + (button["rect"].height - text.get_height()) // 2
            ))

        # Draw size buttons
        for i, size_button in enumerate(size_buttons):
            color = (120, 60, 60) if i == selected_size else (90, 42, 42)
            pygame.draw.rect(screen, color, size_button["rect"])
            text = font.render(size_button["label"], True, (255, 255, 255))
            screen.blit(text, (
                size_button["rect"].x + (button["rect"].width - text.get_width()) // 2,
                size_button["rect"].y + (button["rect"].height - text.get_height()) // 2
            ))

        # Draw type buttons
        for i, type_button in enumerate(type_buttons):
            color = (120, 60, 60) if i == selected_type else (90, 42, 42)
            pygame.draw.rect(screen, color, type_button["rect"])
            text = font.render(type_button["label"], True, (255, 255, 255))
            screen.blit(text, (
                type_button["rect"].x + (button["rect"].width - text.get_width()) // 2,
                type_button["rect"].y + (button["rect"].height - text.get_height()) // 2
            ))

        # Draw condition buttons
        for i, condition_button in enumerate(condition_buttons):
            color = (120, 60, 60) if i == selected_condition else (90, 42, 42)
            pygame.draw.rect(screen, color, condition_button["rect"])
            text = font.render(condition_button["label"], True, (255, 255, 255))
            screen.blit(text, (
                condition_button["rect"].x + (condition_button["rect"].width - text.get_width()) // 2,
                condition_button["rect"].y + (condition_button["rect"].height - text.get_height()) // 2
            ))

        pygame.display.flip()


