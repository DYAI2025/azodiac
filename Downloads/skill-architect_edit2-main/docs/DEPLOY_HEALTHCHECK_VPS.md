# Deployment Guide: Architecture Health-Check VPS

This document outlines the deployment and configuration of the server-mediated API probing feature for the Omni Architecture Brief Engine.

## 1. Overview
The Health-Check VPS acts as a secure mediator for probing internal or external API endpoints. To prevent CORS issues and protect infrastructure, the Architecture Editor (browser) never probes URLs directly. Instead, it sends a probing request to this VPS, which executes the checks and returns a unified health report.

## 2. Prerequisites
- **Python 3.9+**
- **Publicly accessible VPS** (e.g., DigitalOcean, Hetzner, AWS)
- **Nginx** (for HTTPS termination and reverse proxy)
- **SSL Certificate** (e.g., via Certbot/Let's Encrypt)

## 3. Installation

1. **Clone the script** to your VPS:
   ```bash
   # Copy scripts/live_api_health_server.py to your server
   ```

2. **Install dependencies**:
   ```bash
   pip install fastapi uvicorn httpx
   ```

## 4. Configuration (Environment Variables)

The server is configured via environment variables. Create a `.env` file or export them in your systemd unit:

| Variable | Description | Example |
|----------|-------------|---------|
| `HEALTHCHECK_BEARER_TOKEN` | **Required.** Token for the editor to access this VPS. | `your-secure-shared-secret` |
| `HEALTHCHECK_BASE_URL` | Default base URL for relative paths in the architecture. | `https://api.myapp.com` |
| `HEALTHCHECK_ALLOWED_HOSTS` | Comma-separated list of hosts the VPS is allowed to probe. | `api.myapp.com,auth.myapp.com` |
| `HEALTHCHECK_UPSTREAM_TOKEN` | Optional token the VPS sends to the target APIs. | `backend-service-secret` |
| `HEALTHCHECK_TIMEOUT_SECONDS`| Timeout for individual API probes. Default: `10`. | `5` |

## 5. Deployment with Systemd

Create a unit file at `/etc/systemd/system/arch-health.service`:

```ini
[Unit]
Description=Architecture Health-Check Server
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/opt/arch-health
Environment="HEALTHCHECK_BEARER_TOKEN=your-token"
Environment="HEALTHCHECK_ALLOWED_HOSTS=api.myapp.com"
ExecStart=/usr/local/bin/uvicorn live_api_health_server:app --host 127.0.0.1 --port 8000

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable --now arch-health
```

## 6. Nginx Proxy Configuration (HTTPS)

Configure Nginx to serve the app over HTTPS.

```nginx
server {
    listen 443 ssl;
    server_name health.myapp.com;

    ssl_certificate /etc/letsencrypt/live/health.myapp.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/health.myapp.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## 7. Security Disclaimer
- **Network Isolation:** Ensure the VPS resides in a network segment that has network-level access (VPN/VPC) to the target APIs it needs to probe.
- **Zero Trust:** Always use `HEALTHCHECK_BEARER_TOKEN` to ensure only authorized users of your Architecture Editor can trigger probes.
- **Host Allowlisting:** Use `HEALTHCHECK_ALLOWED_HOSTS` to prevent the VPS from being used as a generic proxy to scan external networks.
