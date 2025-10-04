# WireGuard Mesh Manager

WireGuard Mesh Manager is a lightweight web interface designed to easily manage a **WireGuard infrastructure** (nodes and users), automatically generate configuration files, and download them.

---

## ✨ Features

- **Simple web interface** built with FastAPI and HTML/CSS.
- **Node management**:
  - Add nodes with public IP, port, MTU, and VPN IP.
  - Update public IP and VPN IP (RFC 1918).
  - Delete nodes.
- **User (peer) management**:
  - Add users with VPN IP (RFC 1918) and MTU.
  - Update VPN IP.
  - Delete users.
- **Automatic WireGuard key generation** (private/public keys). Pre-shared keys (PSK) are not supported yet.
- **Configuration file generation** for each node and user:
  - Includes options like `PersistentKeepalive`, `Endpoint`, and `MTU`.
- Persistent data storage using **SQLite**.
- **Containerizable application**: Internal port 8000 (tested with Podman).

---

## 📂 Project Structure
```bash
.
├── app/
│   ├── __init__.py       # Initialization file
│   ├── main.py           # FastAPI entry point + routes
│   ├── crud.py           # SQLite database access
│   ├── wireguard.py      # Key and configuration generation
│   ├── wgmanager.py      # CLI orchestration
│   ├── templates/        # HTML pages (nodes, users, overview)
│   └── static/           # CSS, favicon, assets
├── data/                 # Persistent volume (DB + configs)
├── requirements.txt      # Python dependencies
├── Dockerfile            # Python + wireguard-tools image
└── README.md             # Project documentation
```

## Disclaimer : 
If you are on Docker, ~~just use Podman for more safety~~, joking 😄 — when you type a command, just replace the word `podman` with `docker`.

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/CallmeVRM/wireguard-mesh-manager.git
cd wireguard-mesh-manager
```

### 2. Build the container
```bash
podman build -t wireguard-mesh-manager .
```

### 3. Run the container from a local image

#### Podman Version
```bash
docker run -d \
  -p 8000:8000 \
  --name wireguard-mesh-manager \
  -v $(pwd)/data:/data \
  wireguard-mesh-manager
```

### 4. Access the application
Open your browser and navigate to: http://localhost:8000

podman login
podman tag localhost/wireguard-mesh-manager:latest <your_username_or_org>/wireguard-mesh-manager:latest
podman push <your_username_or_org>/wireguard-mesh-manager:latest
podman pull docker.io/<your_username_or_org>/wireguard-mesh-manager:latest

PS : If you’ve enabled 2FA on Docker Hub (and you should do it), you must use a Personal Access Token instead of your password when logging in via docker login.

---

## Use it as a container :
### Download the Container Image
If you prefer to download the pre-built container image, you can use the following command:

### 3. Run the container from a remote image

```bash
docker run -d \
  -p 8000:8000 \
  --name wireguard-mesh-manager \
  -v $(pwd)/data:/data \
  callmevrm/wireguard-mesh-manager
```

```bash
podman run -d \
  -p 8000:8000 \
  --name wg-mesh-manager \
  -v $(pwd)/data:/data \
  docker.io/callmevrm/wireguard-mesh-manager:latest
```

### 4. Access the application
Open your browser and navigate to: http://localhost:8000


## 📜 License
This project is licensed under the MIT License.


## 🤝 Contributing
Contributions are welcome! Feel free to open issues or submit pull requests to improve the project.

##  📧 Contact
For questions or support, contact hamadene.lotfi@gmail.com
