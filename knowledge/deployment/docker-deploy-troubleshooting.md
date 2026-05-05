# Docker Deploy Troubleshooting

## Scenario

适用于使用 Docker 或 Docker Compose 部署企业应用时，构建失败、容器启动失败、健康检查失败或服务无法访问的场景。

## Symptoms

- `docker compose up -d --build` 失败。
- 容器状态为 restarting、unhealthy 或 exited。
- `/health` 无法访问。

## Possible Causes

- 镜像构建依赖下载失败。
- 环境变量、端口映射或 volume 配置错误。
- 应用启动慢，健康检查过早执行。
- 容器内服务监听地址不是 `0.0.0.0`。

## Troubleshooting Steps

1. 查看 `docker compose ps` 和 `docker compose logs --tail=100`。
2. 确认端口映射和容器启动命令。
3. 检查 `.env` 是否存在且变量正确。
4. 确认 volume 目录权限。
5. 使用 `curl http://127.0.0.1:8000/health` 验证服务状态。

## Required Information

- Dockerfile、docker-compose.yml 和 .env 脱敏内容
- 容器日志和健康检查输出
- 服务器系统、Docker 版本和端口占用情况

## Escalation Criteria

- 构建和配置正常但容器持续异常退出。
- 依赖服务或服务器运行环境疑似异常。
