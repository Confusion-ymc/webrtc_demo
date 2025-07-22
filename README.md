# WebRTC Audio/Video Chat Demo

This is a full-featured, self-hosted WebRTC video chat application built with Python, FastAPI, and modern web technologies. It provides a multi-user chat room experience that works across different networks, including mobile (5G/LTE) and strict corporate firewalls, thanks to its integrated STUN/TURN server.

![image](https://github.com/user-attachments/assets/e2b4e57e-832b-468b-877c-13713111819b)


## ✨ Core Features

- **Multi-User Video & Audio Chat**: Real-time communication between multiple peers.
- **Secure & Modern Backend**: Built with FastAPI and WebSockets for signaling.
- **Self-Hosted STUN/TURN Server**: Integrated `coturn` server to ensure connectivity across various network types (NAT traversal), including symmetric NAT.
- **Secure Connections**: Uses HTTPS for the web server and WSS (Secure WebSockets) for signaling, enabling camera/microphone access on all modern browsers, including mobile.
- **Dockerized for Easy Deployment**: Comes with a `Dockerfile` and `docker-compose.yml` for one-command deployment.
- **Responsive UI**: The user interface is optimized for both desktop and mobile screens.
- **Modern Python Tooling**: Uses `uv` for fast dependency management defined in `pyproject.toml`.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.11+, FastAPI, Uvicorn, WebSockets
- **Frontend**: HTML5, CSS3, Vanilla JavaScript (ES6+), WebRTC API
- **Infrastructure & Deployment**: Docker, Docker Compose, Coturn (STUN/TURN Server)

---

## ⚙️ How It Works

The application architecture separates the **Signaling** process from the **Media** flow.

1.  **Signaling Server (FastAPI + WebSockets)**: When a user joins a room, they connect to the FastAPI server via a Secure WebSocket (WSS). The server acts as a "switchboard operator," introducing new users to existing users in the room. It is responsible for passing signaling messages (like SDP Offers/Answers and ICE Candidates) between peers, but it **does not process any audio or video streams**.

2.  **ICE Framework (STUN & TURN)**:
    -   **STUN (Session Traversal Utilities for NAT)**: The `coturn` server first acts as a STUN server. It helps clients discover their public IP address and the type of NAT they are behind. In many cases (like home Wi-Fi), this is enough to establish a direct peer-to-peer connection.
    -   **TURN (Traversal Using Relays around NAT)**: If a direct connection fails (e.g., due to a symmetric NAT on a mobile network), the `coturn` server acts as a TURN relay. All media traffic is then relayed through the server, ensuring a connection can always be established. This guarantees robustness at the cost of higher server bandwidth usage and slightly increased latency.

3.  **Peer-to-Peer Connection (WebRTC)**: Once signaling is complete, the clients (browsers) attempt to form a direct peer-to-peer connection to stream audio and video to each other. If this fails, they use the TURN server as a fallback.

---

## 🚀 Deployment Guide

Follow these steps to deploy the application to a public server.

### Prerequisites

- A server with a public IP address.
- A domain name (e.g., `YOUR_DOMAIN.COM`) pointing to your server's public IP.
- Docker and Docker Compose installed on the server.
- Git installed on the server.

### Step 1: Clone the Repository

```bash
git clone <your-repository-url>
cd <your-repository-directory>
```

### Step 2: Configuration

You must configure your domain name and TURN credentials in two files.

1.  **Configure Docker Compose (`docker-compose.yml`)**:
    Update the `coturn` service command with your domain and a secure password.

    ```yaml
    # docker-compose.yml
    command:
      # ... other options
      - --realm=YOUR_DOMAIN.COM       # <-- IMPORTANT: Replace with your domain
      - --external-ip=YOUR_DOMAIN.COM # <-- IMPORTANT: Replace with your domain
      # Set a secure user and password for TURN
      - --user=myuser:mypassword # <-- CHANGE THIS
    ```

2.  **Configure Frontend (`index.html`)**:
    Update the `RTCPeerConnection` configuration with your domain and TURN credentials.

    ```javascript
    // index.html
    const pc = new RTCPeerConnection({
        iceServers: [
            { urls: 'stun:YOUR_DOMAIN.COM:3478' },
            {
                urls: 'turn:YOUR_DOMAIN.COM:3478',
                username: 'myuser',       // <-- CHANGE THIS
                credential: 'mypassword'  // <-- CHANGE THIS
            }
        ]
    });
    ```

### Step 3: Firewall Configuration

Ensure your server's firewall allows traffic on the following ports:
- **TCP 8080**: For the main web application (HTTPS).
- **UDP 3478**: For STUN and TURN services.
- **TCP 3478**: For STUN and TURN services (optional, but recommended).

### Step 4: Launch the Application

Run the following command in your project directory:

```bash
docker-compose up --build -d
```

Your video chat application is now live and accessible at `https://YOUR_DOMAIN.COM:8080`.

---

## 💻 Local Development

To run the application on your local machine for development:

1.  **Create a virtual environment and install dependencies**:
    ```bash
    # Create venv
    python -m venv .venv
    source .venv/bin/activate

    # Install uv
    pip install uv

    # Install dependencies from pyproject.toml
    uv pip install -e .
    ```

2.  **Generate Self-Signed Certificates**:
    The application requires HTTPS. You can generate a local certificate using `openssl`:
    ```bash
    openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365 -subj "/CN=localhost"
    ```

3.  **Run the Server**:
    You can use the VS Code launch configuration (`.vscode/launch.json`) or run directly from the terminal:
    ```bash
    uvicorn main:app --host 0.0.0.0 --port 8080 --reload --ssl-keyfile ./key.pem --ssl-certfile ./cert.pem
    ```

4.  **Access the App**:
    Open your browser and navigate to `https://localhost:8080`. You will need to accept the browser's security warning about the self-signed certificate.

> **Note**: The TURN functionality cannot be fully tested on `localhost`, as it requires a public IP address.

---

## 📁 Project Structure

```
.
├── .vscode/                # VS Code launch configuration
│   └── launch.json
├── cert.pem                # SSL certificate (generated)
├── key.pem                 # SSL private key (generated)
├── Dockerfile              # Docker instructions for the FastAPI app
├── docker-compose.yml      # Docker Compose for multi-container deployment
├── index.html              # Main frontend file (HTML, CSS, JS)
├── main.py                 # FastAPI backend and WebSocket signaling logic
├── pyproject.toml          # Python project definition and dependencies
└── README.md               # This file
```
