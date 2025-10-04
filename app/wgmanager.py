# app/wgmanager.py
import argparse
import sys
from . import crud, wireguard

# Command to list all nodes
def cmd_list_nodes(args):
    """
    Lists all nodes stored in the database.
    Arguments:
        args : Command-line arguments (not used here).
    Returns:
        None
    """
    rows = crud.list_nodes()
    for r in rows:
        print(f"{r[0]:>3}  {r[1]:<20}  public={r[2] or '-':<16}  vpn={r[3] or '-':<14}  port={r[4] or '-'}  mtu={r[5] or '-'}")

def cmd_list_users(args):
    """
    Lists all users stored in the database.
    Arguments:
        args : Command-line arguments (not used here).
    Returns:
        None
    """    
    rows = crud.list_users()
    for r in rows:
        print(f"{r[0]:>3}  {r[1]:<20}  vpn={r[2] or '-':<14}  mtu={r[3] or '-'}")

def cmd_update_ip(args):
    """
    Updates the public IP address of a node.
    Arguments:
        args : Command-line arguments containing 'name' (node name) and 'ip' (new public IP).
    Returns:
        int : Exit code (0 for success, 2 for failure).
    """    
    name = args.name
    ip = args.ip
    node = crud.get_node_by_name(name)
    if not node:
        print(f"No node named {name}", file=sys.stderr)
        return 2
    crud.update_node_ip(node[0], ip)
    print(f"Updated {name} public_ip -> {ip}")
    return 0

def cmd_update_vpn(args):
    """
    Updates the VPN IP address of a node or user.
    Arguments:
        args : Command-line arguments containing 'name' (node/user name) and 'vpn' (new VPN IP).
    Returns:
        int : Exit code (0 for success, 2 for failure).
    """    
    name = args.name
    vpn = args.vpn
    node = crud.get_node_by_name(name)
    if node:
        crud.update_node_vpn_ip(node[0], vpn)
        print(f"Updated node {name} vpn_ip -> {vpn}")
        return 0
    user = crud.get_user_by_name(name)
    if user:
        crud.update_user_vpn_ip(user[0], vpn)
        print(f"Updated user {name} vpn_ip -> {vpn}")
        return 0
    print(f"No node or user named {name}", file=sys.stderr)
    return 2

def cmd_genmesh(args):
    """
    Generates WireGuard configuration files for all nodes and users.
    Arguments:
        args : Command-line arguments (not used here).
    Returns:
        int : Exit code (0 for success).
    """    
    wireguard.generate_configs()
    print("Configs generated in ./data/wireguard_config")
    return 0

def main():
    """
    Main entry point for the CLI application.
    Defines and parses command-line arguments, and executes the corresponding command.
    Returns:
        int : Exit code (0 for success, 1 for invalid command).
    """    
    parser = argparse.ArgumentParser(prog="wgmanager", description="WG Manager CLI")
    sub = parser.add_subparsers(dest="cmd")

    # Subcommand to list nodes
    p = sub.add_parser("list-nodes")
    p.set_defaults(func=cmd_list_nodes)

    # Subcommand to list users
    p = sub.add_parser("list-users")
    p.set_defaults(func=cmd_list_users)

    # Subcommand to update the public IP of a node
    p = sub.add_parser("update-ip")
    p.add_argument("--name", required=True)
    p.add_argument("--ip", required=True)
    p.set_defaults(func=cmd_update_ip)

    # Subcommand to update the VPN IP of a node or user
    p = sub.add_parser("update-vpn")
    p.add_argument("--name", required=True)
    p.add_argument("--vpn", required=True)
    p.set_defaults(func=cmd_update_vpn)

    # Subcommand to generate WireGuard configuration files
    p = sub.add_parser("genmesh")
    p.set_defaults(func=cmd_genmesh)

    # Parse arguments and execute the corresponding command
    args = parser.parse_args()
    if not hasattr(args, "func"):
        parser.print_help()
        return 1
    return args.func(args)

# Entry point for the script
if __name__ == "__main__":
    raise SystemExit(main())
