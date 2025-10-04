import subprocess
from pathlib import Path
from app import crud  # ✅ IMPORT PACKAGÉ

# Directory to store generated WireGuard configuration files
OUTPUT_DIR = "/data/wireguard_config"
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

def gen_keypair():
    """
    Generates a WireGuard key pair (private and public keys).
    Uses subprocess to execute 'wg genkey' and 'wg pubkey' commands.
    Returns:
        private : Private key as a string.
        public : Public key as a string.
    """
    private = subprocess.check_output(["wg", "genkey"]).decode().strip()
    public  = subprocess.check_output(["wg", "pubkey"], input=private.encode()).decode().strip()
    return private, public

def ensure_keys():
    """
    Ensures that all nodes and users have private and public keys.
    If keys are missing, they are generated and stored in the database.
    """
    # Generate keys for nodes if missing    
    for n in crud.list_nodes():
        if not n["private_key"] or not n["public_key"]:
            priv, pub = gen_keypair()
            conn = crud.get_conn()
            conn.execute("UPDATE nodes SET private_key=?, public_key=? WHERE id=?", (priv, pub, n["id"]))
            conn.commit(); conn.close()

    # Generate keys for users if missing    
    for u in crud.list_users():
        if not u["private_key"] or not u["public_key"]:
            priv, pub = gen_keypair()
            conn = crud.get_conn()
            conn.execute("UPDATE users SET private_key=?, public_key=? WHERE id=?", (priv, pub, u["id"]))
            conn.commit(); conn.close()

def _val(row, key, default=None):
    """
    Helper function to retrieve a value from a dictionary or row object.
    Returns a default value if the key is missing or the value is None/empty.
    Arguments:
        row : Dictionary or row object.
        key : Key to retrieve the value for.
        default : Default value to return if the key is missing or empty.
    Returns:
        Value associated with the key or the default value.
    """    
    v = row.get(key) if hasattr(row, "get") else row[key]
    return v if v not in (None, "") else default

def _append_endpoint_and_keepalive(lines, public_ip, port):
    """
    Appends the 'Endpoint' and 'PersistentKeepalive' configuration to a list of lines.
    Arguments:
        lines : List of configuration lines to append to.
        public_ip : Public IP address of the peer.
        port : Port of the peer.
    """    
    if public_ip and port not in (None, ""):
        lines.append(f"Endpoint = {public_ip}:{port}")
    lines.append("PersistentKeepalive = 25")
    lines.append("")

def generate_configs():
    """
    Generates WireGuard configuration files for nodes and users.
    Writes 'node-{name}.conf' and 'user-{name}.conf' files to OUTPUT_DIR.
    Configuration details:
        - Nodes ↔ Nodes: AllowedIPs = vpn_ip/32
        - Users → Nodes: AllowedIPs = vpn_ip_node/32 (split tunnel, no full tunnel)
        - Endpoint if public_ip + port are available
        - PersistentKeepalive = 25 for all peers
        - No Pre-Shared Keys (PSK)
    Returns:
        dict : Status and message indicating the result of the operation.
    """
    ensure_keys()  # Ensure all nodes and users have keys
    nodes = list(crud.list_nodes())
    users = list(crud.list_users())

    # Generate configurations for nodes
    for n in nodes:
        name   = _val(n, "name", "noname")
        vpn_ip = _val(n, "vpn_ip", "10.100.10.1")
        port   = _val(n, "port", 51820)
        mtu    = _val(n, "mtu", None)
        priv   = _val(n, "private_key", "<PRIVATE_KEY>")

        lines = [
            "[Interface]",
            f"Address = {vpn_ip}/32",
            f"ListenPort = {port}",
        ]
        if mtu not in (None, ""):
            lines.append(f"MTU = {mtu}")
        lines.append(f"PrivateKey = {priv}")
        lines.append("")

        # Add peers (other nodes)
        for peer in nodes:
            if peer["id"] == n["id"]:
                continue
            peer_pub  = _val(peer, "public_key", "<PEER_PUBLIC_KEY>")
            peer_vip  = _val(peer, "vpn_ip", None)
            peer_pip  = _val(peer, "public_ip", None)
            peer_port = _val(peer, "port", None)
            if peer_vip:
                lines += [
                    "[Peer]",
                    f"PublicKey = {peer_pub}",
                    f"AllowedIPs = {peer_vip}/32",
                ]
                _append_endpoint_and_keepalive(lines, peer_pip, peer_port)

        # Add peers (users)
        for u in users:
            u_pub = _val(u, "public_key", "<PEER_PUBLIC_KEY>")
            u_vip = _val(u, "vpn_ip", None)
            if u_vip:
                lines += [
                    "[Peer]",
                    f"PublicKey = {u_pub}",
                    f"AllowedIPs = {u_vip}/32",
                    "PersistentKeepalive = 25",
                    "",
                ]
        
        # Write node configuration to file
        Path(OUTPUT_DIR, f"node-{name}.conf").write_text("\n".join(lines).strip() + "\n", encoding="utf-8")

    # Generate configurations for users
    for u in users:
        name   = _val(u, "name", "client")
        vpn_ip = _val(u, "vpn_ip", "10.100.10.100")
        mtu    = _val(u, "mtu", None)
        priv   = _val(u, "private_key", "<PRIVATE_KEY>")

        lines = [
            "[Interface]",
            f"Address = {vpn_ip}/32",
        ]
        if mtu not in (None, ""):
            lines.append(f"MTU = {mtu}")
        lines.append(f"PrivateKey = {priv}")
        lines.append("")

        # Add peers (nodes)
        for n in nodes:
            n_pub  = _val(n, "public_key", "<PEER_PUBLIC_KEY>")
            n_vip  = _val(n, "vpn_ip", None)
            n_pip  = _val(n, "public_ip", None)
            n_port = _val(n, "port", None)

            lines.append("[Peer]")
            lines.append(f"PublicKey = {n_pub}")
            lines.append(f"AllowedIPs = {n_vip}/32" if n_vip else "AllowedIPs = 0.0.0.0/32")
            _append_endpoint_and_keepalive(lines, n_pip, n_port)

        # Write user configuration to file
        Path(OUTPUT_DIR, f"user-{name}.conf").write_text("\n".join(lines).strip() + "\n", encoding="utf-8")

    return {"status": "ok", "msg": f"Configurations générées dans {OUTPUT_DIR}"}
