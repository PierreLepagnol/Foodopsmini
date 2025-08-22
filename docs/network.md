# Module réseau

Ce module fournit un serveur websocket minimal pour synchroniser les tours de jeu entre plusieurs clients `cli_pro`.

## Lancer le serveur

```bash
python -m foodops_pro.network.server
```

Le serveur écoute par défaut sur `ws://localhost:8765`.

## Connexion d'un client

L'interface CLI peut se connecter avec l'option `--server` :

```bash
python -m foodops_pro.cli_pro --server ws://localhost:8765
```

À la fin de chaque tour, le client envoie un message `ready`. Lorsque tous les clients sont prêts, le serveur incrémente le numéro de tour et le diffuse à tous les clients connectés.
