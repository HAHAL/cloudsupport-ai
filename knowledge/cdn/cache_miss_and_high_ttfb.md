# CDN Cache Miss 与 High TTFB 排查

## 适用场景

适用于 CDN 命中率低、频繁回源、首字节时间 TTFB 高、静态资源加载慢、边缘节点缓存未生效等问题。

## 常见现象

- 响应头显示 `X-Cache: MISS`、`cf-cache-status: MISS` 或类似未命中标识。
- CDN 命中率下降，源站流量和带宽明显上升。
- 静态文件 TTFB 高，用户感知首包慢。
- 同一个 URL 第一次慢，后续访问变快。
- 带 Query String 的 URL 命中率低。

## 可能原因

- 缓存规则未覆盖目标路径或文件类型。
- 源站响应头包含 `Cache-Control: no-store`、`private`、`max-age=0`。
- URL 携带动态参数导致缓存 key 过于离散。
- Cookie、Authorization Header 或 Vary Header 导致缓存被绕过。
- 文件刚刷新或预热未完成。
- 资源实际是动态内容，不适合长时间缓存。
- 源站响应慢导致 cache miss 时 TTFB 高。

## 排查步骤

1. 获取慢请求 URL，检查响应头中的缓存命中标识、Age、Cache-Control。
2. 在 CDN 控制台确认缓存规则是否匹配该 URL。
3. 检查是否启用了忽略 Query String、参数排序或自定义缓存 key。
4. 检查源站是否返回禁止缓存的 Header。
5. 对比同一 URL 多次访问的 TTFB，判断是否为首次回源慢。
6. 查看 CDN 命中率趋势和源站回源流量趋势。
7. 对热点资源执行预热，观察命中率和 TTFB 是否改善。
8. 对动态接口不要强行缓存，需评估业务一致性和用户隔离风险。

## 客户需要提供的信息

- 具体慢请求 URL 列表。
- 响应头完整内容。
- CDN 缓存规则截图或配置说明。
- 源站返回的 Cache-Control、Expires、Vary Header。
- 命中率、回源流量和 TTFB 监控截图。
- 是否近期执行过刷新、预热或发布变更。

## 升级专家/研发的条件

- 缓存规则明确匹配但边缘节点持续 MISS。
- 同一资源在部分节点命中，部分节点持续未命中。
- 预热任务显示成功但访问仍 MISS。
- CDN 缓存行为与产品文档说明不一致。
