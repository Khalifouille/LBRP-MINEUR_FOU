# Description du script

Le script utilise les bibliothèques `time`, `win32api`, `win32con` et `win32gui` pour interagir avec les fenêtres et les événements de la souris sous Windows. Ce code est conçu pour fonctionner sur les serveurs ayant Zero's Gold Digger 🐔 (Gold Script) comme script présent sur leur serveur Garry's Mod.

## Fonction `find_window(title)`

Cette fonction recherche une fenêtre par son titre. Si la fenêtre n'est pas trouvée, elle lève une exception avec un message d'erreur.

- **title** (str) : Le titre de la fenêtre à rechercher.
- **Retourne** : Le handle de la fenêtre (`hwnd`).

## Fonction `hold_left_click(hwnd, x, y, duration)`

Cette fonction simule un clic gauche maintenu pendant une durée spécifiée à une position (x, y) donnée sur la fenêtre identifiée par `hwnd`.

- **hwnd** (int) : Le handle de la fenêtre.
- **x** (int) : La position x du clic.
- **y** (int) : La position y du clic.
- **duration** (float) : La durée pendant laquelle le clic doit être maintenu (en secondes).

## Bloc principal

Le bloc `if __name__ == "__main__":` est le point d'entrée du script. Il effectue les actions suivantes :

1. Définit le titre de la fenêtre cible.
2. Trouve le handle de la fenêtre avec le titre spécifié.
3. Obtient la position actuelle du curseur de la souris.
4. Définit la durée du clic maintenu.
5. Exécute la fonction `hold_left_click` avec les paramètres spécifiés.

## Compatibilité

Ce script est spécialement conçu pour fonctionner sur les serveurs Garry's Mod qui utilisent le script Zero's Gold Digger 🐔 (Gold Script).

## Exécution en arrière-plan

Le script peut tourner en arrière-plan sans nuire à votre activité en premier plan. Vous pouvez continuer à utiliser votre ordinateur normalement pendant que le script simule les clics dans la fenêtre ciblée.
