#!/bin/bash
# 服务器安全配置脚本 - 减脂PK 部署前执行
# 用法: bash server-security.sh
# 仅支持 CentOS/RHEL 和 Ubuntu/Debian

echo "===== 减脂PK 服务器安全配置 ====="

# 1. 防火墙配置
echo "[1/5] 配置防火墙..."
if command -v ufw &> /dev/null; then
    # Ubuntu/Debian
    ufw default deny incoming
    ufw default allow outgoing
    ufw allow 22/tcp       # SSH
    ufw allow 80/tcp       # HTTP
    ufw allow 443/tcp      # HTTPS
    ufw --force enable
    echo "  ✓ UFW 防火墙已启用，仅放行 22/80/443"
elif command -v firewall-cmd &> /dev/null; then
    # CentOS/RHEL
    firewall-cmd --permanent --add-port=22/tcp
    firewall-cmd --permanent --add-port=80/tcp
    firewall-cmd --permanent --add-port=443/tcp
    firewall-cmd --reload
    echo "  ✓ firewalld 已配置，仅放行 22/80/443"
else
    echo "  ⚠ 未检测到防火墙工具，请手动配置"
fi

# 2. 安装 fail2ban 防暴力破解
echo "[2/5] 安装 fail2ban..."
if command -v apt &> /dev/null; then
    apt update -qq && apt install -y -qq fail2ban
elif command -v yum &> /dev/null; then
    yum install -y epel-release && yum install -y fail2ban
fi
systemctl enable fail2ban
systemctl start fail2ban
echo "  ✓ fail2ban 已安装并启动"

# 3. SSH 加固
echo "[3/5] SSH 加固配置..."
SSH_CONFIG="/etc/ssh/sshd_config"
cp "$SSH_CONFIG" "${SSH_CONFIG}.bak.$(date +%s)"

# 禁止 root 密码登录（保留密钥登录）
sed -i 's/^#*PermitRootLogin.*/PermitRootLogin prohibit-password/' "$SSH_CONFIG"
# 禁止密码认证（仅密钥）
# sed -i 's/^#*PasswordAuthentication.*/PasswordAuthentication no/' "$SSH_CONFIG"
# 修改默认端口（可选，取消注释启用）
# sed -i 's/^#*Port 22/Port 2222/' "$SSH_CONFIG"

systemctl restart sshd 2>/dev/null || systemctl restart ssh
echo "  ✓ SSH 已加固: root 仅密钥登录"
echo "  原配置备份: ${SSH_CONFIG}.bak.*"

# 4. 安装 Docker（如未安装）
echo "[4/5] 检查 Docker..."
if ! command -v docker &> /dev/null; then
    echo "  安装 Docker..."
    curl -fsSL https://get.docker.com | sh
    systemctl enable docker
    systemctl start docker
    echo "  ✓ Docker 已安装"
else
    echo "  ✓ Docker 已安装: $(docker --version)"
fi

if ! command -v docker-compose &> /dev/null; then
    echo "  安装 Docker Compose..."
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    echo "  ✓ Docker Compose 已安装"
else
    echo "  ✓ Docker Compose 已安装"
fi

# 5. 系统更新
echo "[5/5] 系统安全更新..."
if command -v apt &> /dev/null; then
    apt update -qq && apt upgrade -y -qq
elif command -v yum &> /dev/null; then
    yum update -y -q
fi
echo "  ✓ 系统已更新"

echo ""
echo "===== 安全配置完成 ====="
echo ""
echo "已完成的防护措施:"
echo "  1. 防火墙: 仅开放 22(SSH) + 80(HTTP) + 443(HTTPS)"
echo "  2. fail2ban: 自动封禁暴力破解IP"
echo "  3. SSH加固: root禁止密码登录,仅密钥"
echo "  4. Docker: 已安装并启动"
echo "  5. 系统: 已更新到最新"
echo ""
echo "下一步:"
echo "  1. git clone 你的仓库"
echo "  2. cp .env.example .env && vi .env (改密码!)"
echo "  3. docker-compose up -d --build"
echo "  4. 配置 DNS A记录指向本服务器IP"
echo "  5. certbot --nginx -d yoyo678.cc.cd (配HTTPS)"
