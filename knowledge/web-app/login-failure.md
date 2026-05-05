# Web App Login Failure

## Scenario

适用于企业后台、SaaS 控制台或管理页面登录失败、返回 `401` / `403`、SSO 登录异常或部分用户无法访问的场景。

## Symptoms

- 登录后提示 Forbidden、Unauthorized 或 Access Denied。
- 部分用户失败，管理员或其他角色正常。
- SSO 登录跳转正常，但回调后无法进入系统。

## Possible Causes

- 用户角色、组织权限或项目授权不足。
- SSO 属性映射、回调地址或登录态 Cookie 异常。
- 访问策略、IP 白名单或安全规则拦截。
- 账号被禁用、租户状态异常或会话过期。

## Troubleshooting Steps

1. 收集失败账号、组织、角色和登录方式。
2. 检查登录接口状态码、request_id 和响应体。
3. 对比成功账号和失败账号权限差异。
4. 检查 SSO 配置、回调 URL、Cookie 和会话状态。
5. 如涉及访问策略，确认来源 IP、设备和浏览器环境。

## Required Information

- 受影响账号、租户和角色
- 登录时间、request_id 和截图
- 浏览器、网络环境和复现步骤
- SSO 或账号体系配置变更记录

## Escalation Criteria

- 权限配置无异常但登录仍稳定失败。
- 多租户、多账号或关键客户范围受影响。
