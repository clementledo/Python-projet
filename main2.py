from game_state import GameState
from views.terminal_view import TerminalView

def main():
    # Initialiser l'état du jeu
    game_state = GameState(use_terminal_view=True)
    
    # Charger la vue terminale
    terminal_view = TerminalView(game_state)

    # Lancer le jeu via la vue terminale
    try:
        terminal_view.run()
    except KeyboardInterrupt:
        print("\nJeu terminé. Merci d'avoir joué !")
    except Exception as e:
        print(f"\nUne erreur inattendue est survenue : {e}")

if __name__ == "__main__":
    main()
