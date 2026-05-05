# API Permission Errors

## Scenario

适用于 API 返回 `403 Forbidden`、账号已认证但无权限访问资源、角色策略或组织权限不匹配的场景。

## Symptoms

- 登录或 API 调用返回 `403 Forbidden`。
- 只有部分企业用户、角色或组织成员受影响。
- 管理员账号正常，普通成员账号失败。

## Possible Causes

- 用户角色、组织权限或资源策略不足。
- SSO / IAM / RBAC 映射配置错误。
- IP 白名单、安全策略或访问控制规则拦截。
- 资源属于其他项目、环境或租户。

## Troubleshooting Steps

1. 确认受影响账号、角色、组织和项目范围。
2. 检查用户是否有目标资源或功能权限。
3. 对比管理员账号和失败账号的权限差异。
4. 检查 SSO 属性映射、角色同步和访问策略。
5. 收集 request_id、用户 ID、时间点和错误响应。

## Required Information

- 受影响账号或用户 ID
- 用户角色、组织、项目或租户
- request_id / trace_id
- 登录方式、访问路径和复现步骤

## Escalation Criteria

- 权限配置看起来正确但仍稳定返回 403。
- 角色策略变更后仍无法生效。
