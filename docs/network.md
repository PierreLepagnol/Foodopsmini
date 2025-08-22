# Module réseau FoodOps Pro

Ce module fournit un serveur WebSocket minimaliste permettant de synchroniser les tours entre plusieurs clients `cli_pro`.

## Lancer le serveur

```bash
python -m foodops_pro.network.server
```

Le serveur écoute par défaut sur `ws://localhost:8765` et maintient un compteur de tour commun.

## Utiliser le client

L'interface `cli_pro` peut se connecter au serveur via l'option `--server` :

```bash
python -m foodops_pro.cli_pro --server ws://localhost:8765
```

À la fin de chaque tour, le client envoie un message `ready` au serveur et attend que tous les autres clients soient prêts pour passer au tour suivant.
