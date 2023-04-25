# INFO841_proxy


## Objectif
 
(a reformuler)
Le but de ce projet est de développer un proxy de sécurité pour la communication web en mettant en place un mécanisme qui permet de chiffrer le traffic à l'entrée d'un domaine où le traffic est susceptible d'être écouté et de déchiffrer celui-ci à la sortie.

## Fonctionnalités

- Construction d'un proxy acceptant les requêtes web et les renvoyant vers un proxy de sortie qui fait la requête à leur place
- Implantation d'un mécanisme d'échange de clé d'encryption par clé publique avec utilisation de la librairie de cryptographie RSA
- Utilisation de la clé d'encryption échangée par le mécanisme RSA pour chiffrer le traffic

## Processus

1. Le proxy reçoit les requêtes HTTP d'un navigateur web configuré pour utiliser un proxy
2. Le proxy chiffre ces requêtes avant de les envoyer au proxy de sortie
3. Le proxy de sortie fait la requête HTTP au serveur web à la place du navigateur web
4. Le proxy de sortie reçoit la réponse, la chiffre et la renvoie vers le proxy source
5. Le proxy source renvoie finalement la réponse au navigateur qui affiche la page demandée.
