# WebRTC 音视频聊天应用

这是一个功能齐全、可自托管的 WebRTC 视频聊天应用，基于 Python、FastAPI 和现代 Web 技术构建。它提供了一个多用户聊天室体验，并借助集成的 STUN/TURN 服务器，确保应用能在各种复杂的网络环境下（包括移动网络和严格的公司防火墙）正常工作。

![image](https://github.com/user-attachments/assets/e2b4e57e-832b-468b-877c-13713111819b)


## ✨ 核心功能

- **多用户视频和音频聊天**: 多个参与者之间的实时音视频通信。
- **现代化安全后端**: 基于 FastAPI 和 WebSockets 构建，用于处理信令。
- **自托管 STUN/TURN 服务器**: 集成 `coturn` 服务器，以确保在各种网络类型（NAT）下的连接成功率，包括对称 NAT。
- **安全连接**: Web 服务器使用 HTTPS，信令使用 WSS (Secure WebSockets)，这使得应用能在所有现代浏览器（包括手机浏览器）上获取摄像头和麦克风权限。
- **Docker化便捷部署**: 配备 `Dockerfile` 和 `docker-compose.yml`，可实现一键部署。
- **响应式用户界面**: UI 界面已为桌面和移动端屏幕优化。
- **现代 Python 工具链**: 使用 `uv` 进行快速依赖管理，依赖项在 `pyproject.toml` 中定义。

---

## 🛠️ 技术栈

- **后端**: Python 3.11+, FastAPI, Uvicorn, WebSockets
- **前端**: HTML5, CSS3, 原生 JavaScript (ES6+), WebRTC API
- **基础设施与部署**: Docker, Docker Compose, Coturn (STUN/TURN 服务器)

---

## ⚙️ 工作原理

本应用的架构将 **信令 (Signaling)** 过程与 **媒体 (Media)** 流分离开来。

1.  **信令服务器 (FastAPI + WebSockets)**: 当用户加入房间时，他们通过一个安全的 WebSocket (WSS) 连接到 FastAPI 服务器。服务器扮演“总机接线员”的角色，将新用户介绍给房间内的其他用户。它负责在用户之间传递信令消息（如 SDP Offers/Answers 和 ICE Candidates），但它**不处理任何音视频流**。

2.  **ICE 框架 (STUN & TURN)**:
    -   **STUN (NAT 会话穿越应用程序)**: `coturn` 服务器首先作为 STUN 服务器工作。它帮助客户端发现自己的公网 IP 地址以及所处的 NAT 类型。在许多情况下（如家庭 Wi-Fi），这足以建立一个直接的点对点连接。
    -   **TURN (中继 NAT 穿越)**: 如果直接连接失败（例如，由于移动网络下的对称 NAT），`coturn` 服务器将作为 TURN 中继站。此时，所有的媒体流量都将通过服务器进行转发，从而确保连接总是能够建立。这种方式保证了连接的健壮性，但代价是更高的服务器带宽消耗和略微增加的延迟。

3.  **点对点连接 (WebRTC)**: 一旦信令交换完成，客户端（浏览器）会尝试建立一个直接的点对点连接，以便相互传输音视频流。如果失败，它们会使用 TURN 服务器作为后备方案。

---

## 🚀 部署指南

请按照以下步骤将此应用部署到一台公网服务器上。

### 前提条件

- 一台拥有公网 IP 地址的服务器。
- 一个指向您服务器公网 IP 的域名（例如 `YOUR_DOMAIN.COM`）。
- 服务器上已安装 Docker 和 Docker Compose。
- 服务器上已安装 Git。

### 第 1 步：克隆仓库

```bash
git clone <你的仓库地址>
cd <你的仓库目录>
```

### 第 2 步：配置

您必须在两个文件中配置您的域名和 TURN 凭证。

1.  **配置 Docker Compose (`docker-compose.yml`)**:
    在 `coturn` 服务的启动命令中，更新您的域名和一个安全的密码。

    ```yaml
    # docker-compose.yml
    command:
      # ... 其他选项
      - --realm=YOUR_DOMAIN.COM
      - --external-ip=YOUR_DOMAIN.COM
      # 为 TURN 认证设置一个安全的用户和密码
      - --user=myuser:mypassword # <-- 修改这里
    ```

2.  **配置前端 (`index.html`)**:
    更新 `RTCPeerConnection` 的配置，填入您的域名和 TURN 凭证。

    ```javascript
    // index.html
    const pc = new RTCPeerConnection({
        iceServers: [
            { urls: 'stun:YOUR_DOMAIN.COM:3478' },
            {
                urls: 'turn:YOUR_DOMAIN.COM:3478',
                username: 'myuser',       // <-- 修改这里
                credential: 'mypassword'  // <-- 修改这里
            }
        ]
    });
    ```

### 第 3 步：配置防火墙

请确保您的服务器防火墙允许以下端口的流量：
- **TCP 8080**: 用于主 Web 应用 (HTTPS)。
- **UDP 3478**: 用于 STUN 和 TURN 服务。
- **TCP 3478**: 用于 STUN 和 TURN 服务 (可选，但建议开启)。

### 第 4 步：启动应用

在您的项目目录中，运行以下命令：

```bash
docker-compose up --build -d
```

现在，您的视频聊天应用已经成功部署，可以通过 `https://你的域名:8080` 进行访问。

---

## 💻 本地开发

要在本地计算机上运行此项目以进行开发：

1.  **创建虚拟环境并安装依赖**:
    ```bash
    # 创建 venv
    python -m venv .venv
    source .venv/bin/activate

    # 安装 uv
    pip install uv

    # 从 pyproject.toml 安装依赖
    uv pip install -e .
    ```

2.  **生成自签名证书**:
    应用需要 HTTPS。您可以使用 `openssl` 生成一个本地证书：
    ```bash
    openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365 -subj "/CN=localhost"
    ```

3.  **运行服务器**:
    您可以使用 VS Code 的启动配置 (`.vscode/launch.json`) 或直接从终端运行：
    ```bash
    uvicorn main:app --host 0.0.0.0 --port 8080 --reload --ssl-keyfile ./key.pem --ssl-certfile ./cert.pem
    ```

4.  **访问应用**:
    打开浏览器并访问 `https://localhost:8080`。您需要接受浏览器关于自签名证书的安全警告。

> **注意**: TURN 功能无法在 `localhost` 上进行完整测试，因为它需要一个公网 IP 地址。

---

## 📁 项目结构

```
.
├── .vscode/                # VS Code 启动配置
│   └── launch.json
├── cert.pem                # SSL 证书 (已生成)
├── key.pem                 # SSL 私钥 (已生成)
├── Dockerfile              # FastAPI 应用的 Docker 配置
├── docker-compose.yml      # 用于多容器部署的 Docker Compose 配置
├── index.html              # 主要的前端文件 (HTML, CSS, JS)
├── main.py                 # FastAPI 后端及 WebSocket 信令逻辑
├── pyproject.toml          # Python 项目定义和依赖项
└── README.md               # 英文版说明文档
└── README.zh-CN.md         # 本文档 (中文版说明)
```
