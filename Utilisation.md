

Il y a une convention de nommage a respecter pour ensuite utiliser ansible a fin de déployer les fichiers de configuration sur les noeuds.

Wireguard-Mesh-Manager, génère des fichiers avec un préfix node-xxx.conf, dans mon exemple je vais utiliser les noms des noeuds suivant : 
- node-prod-services-ipv4.conf
- node-prod-databases-ipv4.conf
- node-prod-monitoring-ipv4.conf

### On se rend dans l'onglet Noeuds :
<img width="1852" height="1035" alt="image" src="https://github.com/user-attachments/assets/77a0c938-b218-463c-9602-736c3004033b" />

### On ajoute le nom, l'IP publique, 
<img width="1860" height="999" alt="image" src="https://github.com/user-attachments/assets/23cf98cc-0c33-4caa-a4e1-b0037d17d980" />

### Respectez la RFC pour définir les IP privées dans votre tunnel, et ne pas créer d'overlapping avec les IP privées de vos machines
Dans mon cas, sur azure comme affiché précédemment dans le schéma, mes vm sont connecté a des subnets avec les ip  10.1.0.0/24,10.2.0.0/24,10.3.0.0/24, je suis partie donc sur du 192.168.0.0/24 pour éviter les problèmes.
<img width="1173" height="944" alt="image" src="https://github.com/user-attachments/assets/3cf3e9ce-313a-4140-a364-c6e2fce4c994" />
