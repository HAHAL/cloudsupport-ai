# DNS Resolution Failure 排查

## 适用场景

适用于用户反馈域名无法访问、DNS 解析失败、解析结果不一致、CNAME 未生效、部分地区无法解析等问题。

## 常见现象

- 浏览器提示 `DNS_PROBE_FINISHED_NXDOMAIN` 或 `server IP address could not be found`。
- `dig` 或 `nslookup` 查询无结果、返回 `NXDOMAIN`、`SERVFAIL`。
- 不同地域或不同运营商解析结果不同。
- 修改 DNS 记录后部分用户仍访问旧 IP。
- CDN CNAME 配置后未生效。

## 可能原因

- 域名未注册、已过期或被暂停解析。
- 权威 DNS 记录缺失、记录类型配置错误或线路配置错误。
- NS 服务器未正确设置到域名注册商。
- TTL 缓存未过期，本地递归 DNS 仍返回旧记录。
- CNAME 链路过长或存在循环。
- DNSSEC 配置错误导致校验失败。
- 本地 hosts、企业 DNS 或运营商递归 DNS 缓存异常。

## 排查步骤

1. 使用 `dig domain +trace` 检查从根到权威 DNS 的完整解析链路。
2. 使用 `dig @8.8.8.8 domain`、`dig @114.114.114.114 domain` 对比递归 DNS 结果。
3. 检查注册商处 NS 是否指向正确的权威 DNS。
4. 在 DNS 控制台确认 A、AAAA、CNAME、TXT 等记录是否存在且线路正确。
5. 检查 TTL，判断是否仍处于缓存生效期。
6. 对 CNAME 场景，逐级解析 CNAME，确认最终目标可解析。
7. 若只有个别客户端异常，检查本地 hosts、DNS 缓存和企业网络策略。

## 客户需要提供的信息

- 异常域名和期望解析结果。
- 发生时间、用户地域和运营商。
- `dig`、`nslookup` 输出。
- 当前 DNS 记录配置截图。
- 注册商 NS 配置截图。
- 是否近期修改过 DNS 记录、NS 或 CDN CNAME。

## 升级专家/研发的条件

- 权威 DNS 返回异常或响应不稳定。
- 多地递归 DNS 查询均失败，且配置确认正确。
- DNSSEC 校验异常需要平台侧进一步排查。
- 域名解析行为与控制台配置不一致。
