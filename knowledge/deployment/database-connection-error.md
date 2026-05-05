# Database Connection Error

## Scenario

适用于企业应用连接数据库失败、连接池耗尽、数据库超时或迁移后连接异常的场景。

## Symptoms

- 应用日志出现 connection refused、timeout、too many connections。
- API 返回 500 或 503。
- 高峰期错误率升高。

## Possible Causes

- 数据库地址、端口、账号或密码错误。
- 网络、安全组或防火墙限制。
- 连接池配置不合理。
- 数据库实例负载高或连接数耗尽。

## Troubleshooting Steps

1. 确认数据库连接字符串和环境变量。
2. 在应用服务器上测试数据库连通性。
3. 查看连接池配置、数据库连接数和慢查询。
4. 检查安全组、防火墙和网络策略。
5. 收集应用日志、数据库日志和监控指标。

## Required Information

- 脱敏后的数据库连接配置
- 应用错误日志和时间范围
- 数据库连接数、CPU、内存和慢查询指标
- 最近变更记录

## Escalation Criteria

- 数据库资源或连接数持续达到上限。
- 网络策略或平台侧连接异常无法自助恢复。
