# 生产环境部署文档

## 目录

- [1. 系统要求](#1-系统要求)
- [2. 环境准备](#2-环境准备)
- [3. 部署方式](#3-部署方式)
- [4. 配置指南](#4-配置指南)
- [5. Steel 部署](#5-steel-部署)
- [6. 监控与日志](#6-监控与日志)
- [7. 安全加固](#7-安全加固)
- [8. 性能调优](#8-性能调优)
- [9. 故障排查](#9-故障排查)
- [10. 维护与升级](#10-维护与升级)

## 1. 系统要求

### 1.1 硬件要求

**最小配置**：
- CPU: 2 核
- 内存: 4GB
- 磁盘: 20GB
- 网络: 100Mbps

**推荐配置**：
- CPU: 4 核以上
- 内存: 8GB 以上
- 磁盘: 50GB SSD
- 网络: 1Gbps

### 1.2 软件要求

| 组件 | 版本要求 |
|------|---------|
| 操作系统 | Ubuntu 20.04+ / CentOS 8+ / macOS 12+ |
| Python | 3.12+ |
| pip | 最新版本 |
| Steel | 官方服务或自托管实例 |

### 1.3 依赖服务

- **Steel Browser Service**：浏览器自动化基础设施
- **LLM API**：OpenAI API 或兼容服务
- **反向代理**（可选）：Nginx / Caddy
- **进程管理**（可选）：Supervisor / systemd
- **监控系统**（可选）：Prometheus + Grafana

## 2. 环境准备

### 2.1 创建部署用户

```bash
# 创建专用部署用户
sudo useradd -m -s /bin/bash manuskit
sudo usermod -aG sudo manuskit

# 切换到部署用户
su - manuskit
```

### 2.2 安装 Python 3.12

**Ubuntu/Debian**:
```bash
sudo apt update
sudo apt install -y software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install -y python3.12 python3.12-venv python3.12-dev
```

**CentOS/RHEL**:
```bash
sudo dnf install -y python3.12 python3.12-devel
```

**macOS**:
```bash
brew install python@3.12
```

### 2.3 克隆项目

```bash
# 创建项目目录
cd /opt
sudo mkdir manuskit
sudo chown manuskit:manuskit manuskit
cd manuskit

# 克隆代码（或上传压缩包）
git clone <repository-url> .

# 或从压缩包解压
tar -xzf manuskit.tar.gz
```

### 2.4 创建虚拟环境

```bash
cd /opt/manuskit
python3.12 -m venv venv
source venv/bin/activate

# 升级 pip
pip install --upgrade pip setuptools wheel
```

### 2.5 安装依赖

```bash
pip install -r requirements.txt
```

## 3. 部署方式

### 3.1 方式一：Systemd 服务（推荐）

创建 systemd 服务文件：

```bash
sudo nano /etc/systemd/system/manuskit.service
```

```ini
[Unit]
Description=Manuskit Web Content Extraction Platform
After=network.target

[Service]
Type=simple
User=manuskit
Group=manuskit
WorkingDirectory=/opt/manuskit
Environment="PATH=/opt/manuskit/venv/bin"
ExecStart=/opt/manuskit/venv/bin/gunicorn src.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8080 \
    --timeout 300 \
    --access-logfile /var/log/manuskit/access.log \
    --error-logfile /var/log/manuskit/error.log \
    --log-level info

# 环境变量（生产环境建议使用 EnvironmentFile）
EnvironmentFile=/opt/manuskit/.env

# 重启策略
Restart=always
RestartSec=10s

# 资源限制
LimitNOFILE=65536

[Install]
WantedBy=multi-user.target
```

创建日志目录：
```bash
sudo mkdir -p /var/log/manuskit
sudo chown manuskit:manuskit /var/log/manuskit
```

启动服务：
```bash
# 重新加载 systemd
sudo systemctl daemon-reload

# 启动服务
sudo systemctl start manuskit

# 设置开机自启
sudo systemctl enable manuskit

# 查看状态
sudo systemctl status manuskit

# 查看日志
sudo journalctl -u manuskit -f
```

### 3.2 方式二：Supervisor

安装 Supervisor：
```bash
sudo apt install -y supervisor  # Ubuntu/Debian
sudo yum install -y supervisor  # CentOS/RHEL
```

创建配置文件：
```bash
sudo nano /etc/supervisor/conf.d/manuskit.conf
```

```ini
[program:manuskit]
command=/opt/manuskit/venv/bin/gunicorn src.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8080 \
    --timeout 300
directory=/opt/manuskit
user=manuskit
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/manuskit/app.log
stderr_logfile=/var/log/manuskit/error.log
environment=PATH="/opt/manuskit/venv/bin"
```

启动服务：
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start manuskit
sudo supervisorctl status manuskit
```

### 3.3 方式三：Docker 容器

创建 `Dockerfile`：
```dockerfile
FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY src/ ./src/
COPY .env.example .env

# 暴露端口
EXPOSE 8080

# 启动命令
CMD ["gunicorn", "src.main:app", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8080", \
     "--timeout", "300"]
```

创建 `docker-compose.yml`：
```yaml
version: '3.8'

services:
  manuskit:
    build: .
    container_name: manuskit
    ports:
      - "8080:8080"
    environment:
      - STEEL_BASE_URL=http://steel-service:3000
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - MODEL=gpt-4o-mini
      - MAX_CONCURRENT_TASKS=5
    volumes:
      - ./logs:/var/log/manuskit
    restart: unless-stopped
    networks:
      - manuskit-network

networks:
  manuskit-network:
    driver: bridge
```

启动容器：
```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 3.4 方式四：Kubernetes 部署

创建 `k8s-deployment.yaml`：
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: manuskit
  namespace: default
spec:
  replicas: 3
  selector:
    matchLabels:
      app: manuskit
  template:
    metadata:
      labels:
        app: manuskit
    spec:
      containers:
      - name: manuskit
        image: manuskit:latest
        ports:
        - containerPort: 8080
        env:
        - name: STEEL_BASE_URL
          valueFrom:
            configMapKeyRef:
              name: manuskit-config
              key: steel_base_url
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: manuskit-secrets
              key: openai_api_key
        - name: MAX_CONCURRENT_TASKS
          value: "5"
        resources:
          requests:
            memory: "2Gi"
            cpu: "1"
          limits:
            memory: "4Gi"
            cpu: "2"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 5

---
apiVersion: v1
kind: Service
metadata:
  name: manuskit-service
  namespace: default
spec:
  selector:
    app: manuskit
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080
  type: LoadBalancer

---
apiVersion: v1
kind: ConfigMap
metadata:
  name: manuskit-config
data:
  steel_base_url: "http://steel-service:3000"
  model: "gpt-4o-mini"

---
apiVersion: v1
kind: Secret
metadata:
  name: manuskit-secrets
type: Opaque
stringData:
  openai_api_key: "your-openai-api-key"
```

部署到 K8s：
```bash
kubectl apply -f k8s-deployment.yaml
kubectl get pods -l app=manuskit
kubectl logs -f deployment/manuskit
```

## 4. 配置指南

### 4.1 环境变量配置

生产环境 `.env` 示例：
```bash
# Steel 配置
STEEL_BASE_URL=http://your-steel-server:3000
# 或使用官方 Steel
# STEEL_API_KEY=sk_live_your_api_key_here

# LLM 配置
MODEL=gpt-4o-mini
OPENAI_API_KEY=sk-your-openai-api-key
OPENAI_BASE_URL=https://api.openai.com/v1

# 服务器配置
HOST=0.0.0.0
PORT=8080
MAX_CONCURRENT_TASKS=10

# 日志级别
LOG_LEVEL=INFO
```

### 4.2 Gunicorn 配置

创建 `gunicorn_config.py`：
```python
import multiprocessing

# 服务器绑定
bind = "0.0.0.0:8080"

# Worker 配置
workers = multiprocessing.cpu_count() * 2 + 1  # 推荐公式
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000  # 防止内存泄漏
max_requests_jitter = 50

# 超时配置
timeout = 300  # 5 分钟
graceful_timeout = 30
keepalive = 5

# 日志配置
accesslog = "/var/log/manuskit/access.log"
errorlog = "/var/log/manuskit/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# 进程命名
proc_name = "manuskit"

# 预加载应用
preload_app = True
```

使用配置文件启动：
```bash
gunicorn -c gunicorn_config.py src.main:app
```

### 4.3 Nginx 反向代理

安装 Nginx：
```bash
sudo apt install -y nginx  # Ubuntu/Debian
sudo yum install -y nginx  # CentOS/RHEL
```

创建配置文件 `/etc/nginx/sites-available/manuskit`：
```nginx
upstream manuskit_backend {
    # 负载均衡策略：轮询
    server 127.0.0.1:8080 max_fails=3 fail_timeout=30s;
    # 如果有多个实例
    # server 127.0.0.1:8081 max_fails=3 fail_timeout=30s;
    # server 127.0.0.1:8082 max_fails=3 fail_timeout=30s;
    
    keepalive 32;
}

# HTTP 重定向到 HTTPS
server {
    listen 80;
    server_name your-domain.com;
    
    # Let's Encrypt 验证路径
    location /.well-known/acert-challenge/ {
        root /var/www/certbot;
    }
    
    # 重定向到 HTTPS
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS 配置
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    # SSL 证书配置
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';
    ssl_prefer_server_ciphers on;
    
    # 日志配置
    access_log /var/log/nginx/manuskit_access.log;
    error_log /var/log/nginx/manuskit_error.log;
    
    # 客户端配置
    client_max_body_size 10M;
    client_body_timeout 300s;
    
    # 代理到后端
    location / {
        proxy_pass http://manuskit_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时配置（长时间运行的任务）
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
        
        # WebSocket 支持（如果需要）
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    # 健康检查端点（不记录日志）
    location /health {
        proxy_pass http://manuskit_backend/health;
        access_log off;
    }
    
    # API 文档
    location /docs {
        proxy_pass http://manuskit_backend/docs;
    }
    
    # 静态文件缓存（如果有）
    location /static/ {
        alias /opt/manuskit/static/;
        expires 7d;
        add_header Cache-Control "public, immutable";
    }
    
    # 安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
}
```

启用配置：
```bash
# 创建软链接
sudo ln -s /etc/nginx/sites-available/manuskit /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启 Nginx
sudo systemctl restart nginx
```

### 4.4 SSL 证书（Let's Encrypt）

```bash
# 安装 Certbot
sudo apt install -y certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
```

## 5. Steel 部署

### 5.1 使用官方 Steel

直接配置 API Key：
```bash
STEEL_API_KEY=sk_live_your_api_key_here
```

### 5.2 自托管 Steel

参考 Steel 官方文档部署自托管实例，然后配置：
```bash
STEEL_BASE_URL=http://your-steel-server:3000
```

## 6. 监控与日志

### 6.1 应用日志

**日志文件位置**：
- Systemd: `/var/log/manuskit/`
- Supervisor: `/var/log/manuskit/`
- Docker: `docker logs manuskit`

**日志轮转**（`/etc/logrotate.d/manuskit`）：
```
/var/log/manuskit/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 manuskit manuskit
    sharedscripts
    postrotate
        systemctl reload manuskit > /dev/null 2>&1 || true
    endscript
}
```

### 6.2 Prometheus 监控

安装 Prometheus Python 客户端：
```bash
pip install prometheus-client
```

在 `src/main.py` 中添加指标导出：
```python
from prometheus_client import make_asgi_app, Counter, Histogram, Gauge

# 创建指标
request_count = Counter('manuskit_requests_total', 'Total requests', ['method', 'endpoint'])
task_duration = Histogram('manuskit_task_duration_seconds', 'Task duration')
active_tasks = Gauge('manuskit_active_tasks', 'Number of active tasks')

# 挂载指标端点
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)
```

Prometheus 配置（`prometheus.yml`）：
```yaml
scrape_configs:
  - job_name: 'manuskit'
    scrape_interval: 15s
    static_configs:
      - targets: ['localhost:8080']
    metrics_path: '/metrics'
```

### 6.3 Grafana 仪表板

导入 Grafana 仪表板监控：
- 任务成功率
- 平均执行时间
- 并发任务数
- API 响应时间
- 错误率

## 7. 安全加固

### 7.1 防火墙配置

```bash
# Ubuntu/Debian (UFW)
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# CentOS/RHEL (firewalld)
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

### 7.2 API 限流

使用 Nginx 限流：
```nginx
# 定义限流区域
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

location /api/ {
    limit_req zone=api_limit burst=20 nodelay;
    proxy_pass http://manuskit_backend;
}
```

### 7.3 环境变量安全

```bash
# 设置文件权限
chmod 600 /opt/manuskit/.env
chown manuskit:manuskit /opt/manuskit/.env

# 使用加密存储（推荐）
# 使用 Vault / AWS Secrets Manager 等
```

## 8. 性能调优

### 8.1 系统参数优化

编辑 `/etc/sysctl.conf`：
```bash
# 网络优化
net.core.somaxconn = 65535
net.ipv4.tcp_max_syn_backlog = 8192
net.ipv4.tcp_fin_timeout = 30

# 文件描述符限制
fs.file-max = 100000
```

应用配置：
```bash
sudo sysctl -p
```

### 8.2 应用性能优化

- 增加 Gunicorn workers 数量
- 提高 `MAX_CONCURRENT_TASKS` 配置
- 使用连接池
- 启用缓存（Redis）

## 9. 故障排查

### 9.1 常见问题

**问题 1：服务无法启动**
```bash
# 检查日志
sudo journalctl -u manuskit -n 50

# 检查端口占用
sudo netstat -tulpn | grep 8080

# 检查配置文件
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print(os.getenv('STEEL_BASE_URL'))"
```

**问题 2：Steel 连接失败**
```bash
# 测试 Steel 连接
curl http://steel-server:3000/health

# 检查网络
ping steel-server
telnet steel-server 3000
```

**问题 3：任务执行超时**
- 检查 Gunicorn timeout 配置
- 检查 Nginx proxy_read_timeout
- 增加 LLM API 超时时间

### 9.2 调试模式

临时启用调试：
```bash
# 直接运行（开发模式）
python -m src.main

# 查看详细日志
export LOG_LEVEL=DEBUG
python -m src.main
```

## 10. 维护与升级

### 10.1 备份策略

```bash
# 备份配置
tar -czf manuskit-config-$(date +%Y%m%d).tar.gz /opt/manuskit/.env

# 备份日志
tar -czf manuskit-logs-$(date +%Y%m%d).tar.gz /var/log/manuskit/
```

### 10.2 版本升级

```bash
# 1. 停止服务
sudo systemctl stop manuskit

# 2. 备份当前版本
cp -r /opt/manuskit /opt/manuskit.backup

# 3. 更新代码
cd /opt/manuskit
git pull origin main

# 4. 更新依赖
source venv/bin/activate
pip install -r requirements.txt --upgrade

# 5. 重启服务
sudo systemctl start manuskit

# 6. 验证
curl http://localhost:8080/health
```

### 10.3 回滚策略

```bash
# 如果升级失败，快速回滚
sudo systemctl stop manuskit
rm -rf /opt/manuskit
mv /opt/manuskit.backup /opt/manuskit
sudo systemctl start manuskit
```

## 11. 附录

### 11.1 完整部署检查清单

- [ ] Python 3.12+ 已安装
- [ ] 虚拟环境已创建
- [ ] 依赖已安装
- [ ] 环境变量已配置（`.env`）
- [ ] Steel 服务可访问
- [ ] LLM API 可用
- [ ] Gunicorn 配置正确
- [ ] Systemd/Supervisor 服务已启用
- [ ] Nginx 反向代理已配置
- [ ] SSL 证书已安装
- [ ] 防火墙规则已配置
- [ ] 日志轮转已配置
- [ ] 监控系统已接入
- [ ] 健康检查正常
- [ ] 压力测试通过

### 11.2 性能基准

**单实例性能（4 核 8GB）**：
- 并发任务：5-10
- 平均响应时间：30-120 秒
- 吞吐量：~50 任务/小时

**集群性能（3 实例）**：
- 并发任务：15-30
- 吞吐量：~150 任务/小时

### 11.3 联系支持

- 技术文档：`/docs/ARCHITECTURE.md`
- API 文档：`/docs/API.md`
- 问题反馈：GitHub Issues
