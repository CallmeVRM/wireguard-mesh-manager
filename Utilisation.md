
Veillez à ouvrir le port que vous souhaitez utiliser au niveau du pare-feu.

Il existe une convention de nommage à respecter afin de pouvoir ensuite utiliser Ansible pour déployer automatiquement les fichiers de configuration sur les nœuds.


L’application WireGuard-Mesh-Manager génère des fichiers avec un préfixe de type node-xxx.conf.
Dans cet exemple, j’utilise les noms de nœuds suivants :
` 
`node-prod-services-ipv4.conf`
`node-prod-databases-ipv4.conf`
`node-prod-monitoring-ipv4.conf`

### Accédez à l’onglet Gérer les nœuds :
<img width="1852" height="1035" alt="image" src="https://github.com/user-attachments/assets/77a0c938-b218-463c-9602-736c3004033b" />

### Ajoutez le nom, l’IP publique, l’IP VPN, et laissez le MTU ainsi que le port par défaut.
<img width="1860" height="999" alt="image" src="https://github.com/user-attachments/assets/23cf98cc-0c33-4caa-a4e1-b0037d17d980" />

#### ⚙️ Bonnes pratiques d’adressage.
Respectez la RFC 1918 pour définir les IP privées de votre tunnel, afin d’éviter tout chevauchement (overlapping) avec les IP internes de vos machines.

Dans mon cas, sur Azure, comme indiqué dans le schéma précédent, mes VM sont connectées à des sous-réseaux : `10.1.0.0/24, 10.2.0.0/24 et 10.3.0.0/24`
J’ai donc choisi le réseau 192.168.0.0/24 pour le VPN afin d’éviter tout conflit.
<img width="1173" height="944" alt="image" src="https://github.com/user-attachments/assets/3cf3e9ce-313a-4140-a364-c6e2fce4c994" />

### Passez ensuite à l’onglet Utilisateurs.
<img width="1858" height="998" alt="image" src="https://github.com/user-attachments/assets/584bd6c8-c9ee-4c48-a5b6-fe01666f4abc" />

### Définissez un nom et une IP VPN, toujours dans la plage privée autorisée (RFC 1918).
Je recommande d’utiliser une plage d’adresses différente de celle des nœuds, afin de garder une topologie claire et lisible.
<img width="1860" height="998" alt="image" src="https://github.com/user-attachments/assets/37ef6191-e0a0-4504-99f3-9133885425a8" />

### Vérification de la configuration.
À cette étape, cliquez sur Aperçu pour obtenir une vue d’ensemble de votre infrastructure.
Cela permet de vérifier qu’aucun utilisateur ni nœud n’a été oublié, et que les adresses IP attribuées sont correctes.

Notez que les clés publiques ne sont pas encore visibles tant que les fichiers de configuration n’ont pas été générés.
<img width="1858" height="998" alt="image" src="https://github.com/user-attachments/assets/e966db83-0ca6-44e0-8bea-bb8208347b72" />

### Une fois la configuration validée, retournez sur le dashboard et cliquez sur Générer les fichiers de configuration.
Vous constatez ici que nous avons bien 3 nœuds et 2 utilisateurs :
<img width="1859" height="997" alt="image" src="https://github.com/user-attachments/assets/ce93563c-27a3-4e3a-876e-fb470dba738a" />

En cliquant de nouveau sur Aperçu, vous verrez que les clés publiques ont été générées et associées automatiquement :
<img width="1166" height="359" alt="image" src="https://github.com/user-attachments/assets/6bf2c1a4-670e-40ca-b187-24bf15a2a8ac" />

### 📦 Récupération des fichiers

Pour récupérer vos fichiers de configuration, deux options s’offrent à vous :
- Depuis votre hôte accédez directement au volume monté dans le dossier data/
- Ou cliquez sur Télécharger depuis l’interface.
<img width="1856" height="998" alt="image" src="https://github.com/user-attachments/assets/d7b3dc18-0e33-437a-9ba7-5f370ae17380" />

Vos fichiers de configuration sont maintenant prêts à être utilisés.

Désormais vous pouvez :
- Les uploader manuellement sur chaque nœud, les placer dans /etc/wireguard/ et les renommer (ex. wg0.conf)
- Ou, de manière plus élégante et automatisée, les déployer via un playbook ou un rôle Ansible, parce que, soyons honnêtes, vous n’êtes pas des galériens, mais des fainéants intelligents 😄


---
Bonus : Déploiement via Ansible  > lien vers le repo




