# 减脂PK 部署指南

## 一、推送到 GitHub

```bash
cd F:\weight
git init
git add .
git commit -m "减脂PK 完整项目：Vue3前端 + FastAPI后端 + Docker部署"
git branch -M main
git remote add origin https://github.com/你的用户名/fatloss-pk.git
git push -u origin main
```

## 二、服务器拉取

登录服务器后：
```bash
git clone https://github.com/你的用户名/fatloss-pk.git
cd fatloss-pk
```

## 三、配置环境变量

```bash
cp .env.example .env
vi .env
```

修改以下内容（务必改密码）：
```
DB_ROOT_PASSWORD=换一个强密码
DB_NAME=fatloss_pk
DB_USER=fatloss
DB_PASSWORD=换一个强密码
JWT_SECRET=换一串随机字符串
DOMAIN=yoyo678.cc.cd
```

## 四、启动服务

确保服务器已安装 Docker 和 Docker Compose：
```bash
docker-compose up -d --build
```

等待构建完成后，检查状态：
```bash
docker-compose ps
docker-compose logs -f
```

三个容器都应该是 running 状态：
- fatloss-db (MySQL)
- fatloss-backend (FastAPI)
- fatloss-frontend (Nginx + Vue)

验证：
```bash
curl http://localhost/health    # 应返回 {"status":"ok"}
curl http://localhost/          # 应返回前端 HTML
```

## 五、DNS 解析配置

在你的域名管理面板（yoyo678.cc.cd）添加 DNS 记录：

### A 记录
| 记录类型 | 主机记录 | 记录值 | TTL |
|---------|---------|-------|-----|
| A | @ | 你的服务器公网IP | 600 |

### www CNAME（可选）
| 记录类型 | 主机记录 | 记录值 | TTL |
|---------|---------|-------|-----|
| CNAME | www | yoyo678.cc.cd | 600 |

> ⚠️ 主机记录 `@` 表示根域名 yoyo678.cc.cd 本身。填你服务器的公网 IP。

### 验证 DNS 生效
```bash
ping yoyo678.cc.cd
# 或
nslookup yoyo678.cc.cd
```
解析出的 IP 应该是你服务器的公网 IP。DNS 生效通常需要几分钟到几小时。

## 六、配置 HTTPS（推荐）

安装 certbot 获取免费 SSL 证书：
```bash
# 安装 certbot
apt install -y certbot python3-certbot-nginx

# 获取证书（会自动修改 nginx 配置）
certbot --nginx -d yoyo678.cc.cd

# 或者使用 docker 方式
docker run -it --rm -v /etc/letsencrypt:/etc/letsencrypt \
  -v /var/www/certbot:/var/www/certbot \
  certbot/certbot certonly --webroot -w /var/www/certbot \
  -d yoyo678.cc.cd
```

证书自动续期：
```bash
# 添加 crontab
echo "0 3 * * * certbot renew --quiet" >> /etc/crontab
```

## 七、防火墙放行

确保服务器防火墙放行 80 和 443 端口：
```bash
# Ubuntu/Debian
ufw allow 80
ufw allow 443
ufw reload

# CentOS
firewall-cmd --permanent --add-port=80/tcp
firewall-cmd --permanent --add-port=443/tcp
firewall-cmd --reload
```

## 完整启动流程速查

```bash
# 1. 拉取代码
git clone https://github.com/你的用户名/fatloss-pk.git
cd fatloss-pk

# 2. 配置环境
cp .env.example .env
vi .env  # 改密码和密钥

# 3. 启动
docker-compose up -d --build

# 4. 检查
docker-compose ps
curl http://localhost/health

# 5. 去域名面板加 A 记录指向服务器IP
# 6. 等 DNS 生效，访问 http://yoyo678.cc.cd
# 7. （可选）配 HTTPS
```
