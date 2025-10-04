from pathlib import Path
import shutil

from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse, FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import io, zipfile
from fastapi.responses import StreamingResponse

from app import crud
from app import wireguard

# Define base directories for templates, static files, and configuration
BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

# Define data directory and configuration directory
DATA_DIR = Path("/data")
CONFIG_DIR = DATA_DIR / "wireguard_config"
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

# Initialize FastAPI application
app = FastAPI()

# Mount static files directory for serving assets
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Initialize Jinja2 templates for rendering HTML pages
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

@app.on_event("startup")
def startup():
    """
    Startup event to initialize the database and ensure the configuration directory exists.
    """
    crud.init_db()
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

# Pages
@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    """
    Render the dashboard page with a list of nodes and users.
    """
    nodes = crud.list_nodes()
    users = crud.list_users()
    return templates.TemplateResponse("index.html", {"request": request, "nodes": nodes, "users": users})


@app.get("/nodes", response_class=HTMLResponse)
def page_nodes(request: Request):
    """
    Render the nodes page with a list of all nodes.
    """
    nodes = crud.list_nodes()
    return templates.TemplateResponse("nodes.html", {"request": request, "nodes": nodes})

@app.get("/users", response_class=HTMLResponse)
def page_users(request: Request):
    """
    Render the users page with a list of all users.
    """
    users = crud.list_users()
    return templates.TemplateResponse("users.html", {"request": request, "users": users})

@app.get("/overview", response_class=HTMLResponse)
def page_overview(request: Request):    
    """
    Render the overview page with a summary of nodes and users.
    """
    nodes = crud.list_nodes()
    users = crud.list_users()
    return templates.TemplateResponse(
        "overview.html",
        {"request": request, "nodes": nodes, "users": users}
    )

# Nodes CRUD
@app.post("/nodes/add")
def add_node(name: str = Form(...), public_ip: str = Form(""), port: str = Form("51820"),
             mtu: str = Form(None), vpn_ip: str = Form(None)):
    
    """
    Add a new node to the database.
    Arguments:
        name : Name of the node.
        public_ip : Public IP address of the node.
        port : Port used by the node (default: 51820).
        mtu : Maximum Transmission Unit (optional).
        vpn_ip : VPN IP address of the node (optional).
    """    
        # Validate and convert port and mtu to integers if provided
    try:
        port_val = int(port)
    except Exception:
        port_val = 51820
    mtu_val = None
    if mtu not in (None, "", "-", "None"):
        try:
            mtu_val = int(mtu)
        except Exception:
            mtu_val = None
    crud.create_node(name=name, public_ip=public_ip, port=port_val, mtu=mtu_val, vpn_ip=vpn_ip)
    return RedirectResponse("/nodes?notice=node-added", status_code=303)

@app.post("/nodes/update-ip")
def update_node_public_ip(node_id: int = Form(...), new_ip: str = Form(...)):
    """
    Update the public IP address of a node.
    Arguments:
        node_id : ID of the node to update.
        new_ip : New public IP address.
    """    
    crud.update_node_public_ip(node_id, new_ip)
    return RedirectResponse("/nodes?notice=ip-updated", status_code=303)

@app.post("/nodes/update-vpn-ip")
def update_node_vpn_ip(node_id: int = Form(...), new_vpn_ip: str = Form(...)):
    """
    Update the VPN IP address of a node.
    Arguments:
        node_id : ID of the node to update.
        new_vpn_ip : New VPN IP address.
    """    
    crud.update_node_vpn_ip(node_id, new_vpn_ip)
    return RedirectResponse("/nodes?notice=vpn-updated", status_code=303)

# Users CRUD
@app.post("/users/add")
def add_user(name: str = Form(...), mtu: str = Form(None), vpn_ip: str = Form(None)):
    """
    Add a new user to the database.
    Arguments:
        name : Name of the user.
        mtu : Maximum Transmission Unit (optional).
        vpn_ip : VPN IP address of the user (optional).
    """ 
    mtu_val = None
    if mtu not in (None, "", "-", "None"):
        try:
            mtu_val = int(mtu)
        except Exception:
            mtu_val = None
    crud.create_user(name=name, mtu=mtu_val, vpn_ip=vpn_ip)
    return RedirectResponse("/users?notice=user-added", status_code=303)

@app.post("/users/update-vpn-ip")
def update_user_vpn_ip(user_id: int = Form(...), new_vpn_ip: str = Form(...)):
    """
    Update the VPN IP address of a user.
    Arguments:
        user_id : ID of the user to update.
        new_vpn_ip : New VPN IP address.
    """    
    crud.update_user_vpn_ip(user_id, new_vpn_ip)
    return RedirectResponse("/users?notice=user-vpn-updated", status_code=303)

# Configuration management
@app.post("/genmesh")
def genmesh():
    """
    Generate WireGuard configuration files for all nodes and users.
    """
    # Generate configurations    
    wireguard.generate_configs()
    return RedirectResponse("/?notice=gen-ok", status_code=303)

@app.post("/configs/clear")
def clear_configs():
    """
    Clear all configuration files (.conf and .zip) from the configuration directory.
    """    
    for p in CONFIG_DIR.glob("*"):
        if p.is_file() and p.suffix in (".conf", ".zip"):
            try: p.unlink()
            except Exception: pass
    return RedirectResponse("/?notice=configs-cleared", status_code=303)

@app.get("/configs/all.zip")
def download_zip():
    """
    Create and return a ZIP file containing all configuration files.
    """    
    # Create a ZIP file in memory
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for p in CONFIG_DIR.glob("*.conf"):
            zf.write(p, arcname=p.name)
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=wireguard-configs.zip"}
    )

@app.post("/reset-db")
def reset_db():
    """
    Reset the database by dropping all tables and recreating them.
    Also clears all configuration files.
    """    
    conn = crud.get_conn(); c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS nodes")
    c.execute("DROP TABLE IF EXISTS users")
    conn.commit(); conn.close()
    crud.init_db()
    for p in CONFIG_DIR.glob("*"):
        if p.is_file():
            try: p.unlink()
            except Exception: pass
    return RedirectResponse("/?notice=db-reset", status_code=303)

@app.post("/nodes/delete")
def delete_node(node_id: int = Form(...)):
    """
    Delete a node from the database.
    Arguments:
        node_id : ID of the node to delete.
    """    
    crud.delete_node(node_id)
    return RedirectResponse("/nodes?notice=node-deleted", status_code=303)

@app.post("/users/delete")
def delete_user(user_id: int = Form(...)):
    """
    Delete a user from the database.
    Arguments:
        user_id : ID of the user to delete.
    """    
    crud.delete_user(user_id)
    return RedirectResponse("/users?notice=user-deleted", status_code=303)
