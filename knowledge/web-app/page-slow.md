# Web App Page Slow

## Scenario

适用于企业后台页面加载慢、接口等待时间长、首屏慢、导出任务慢或控制台操作卡顿的场景。

## Symptoms

- 页面加载时间明显增加。
- 浏览器 Network 中接口耗时高。
- 日志中出现 request_time 或 upstream_response_time 升高。

## Possible Causes

- 后端接口响应慢。
- 数据库查询、报表导出或第三方依赖慢。
- 前端资源过大或缓存策略不合理。
- 网络链路、代理或网关配置导致延迟。

## Troubleshooting Steps

1. 使用浏览器开发者工具拆分 DNS、TCP、TLS、TTFB 和下载耗时。
2. 找出慢接口和慢资源。
3. 查看应用日志、慢查询日志和依赖服务监控。
4. 对比不同账号、租户、区域和时间段。
5. 确认是否近期发布、配置变更或数据量增长。

## Required Information

- 页面 URL、慢接口 URL 和 HAR 文件
- request_id、时间范围和复现步骤
- 用户账号、租户和数据规模
- 浏览器版本、网络环境和截图

## Escalation Criteria

- 慢请求集中在后端接口或数据库依赖。
- 多用户或关键业务页面持续变慢。
