# Kubernetes Pod Pending 排查

## 适用场景

适用于 Kubernetes 集群中 Pod 长时间处于 `Pending` 状态，业务无法调度或发布卡住的情况。

## 常见现象

- `kubectl get pod` 显示 Pod 状态为 `Pending`。
- `kubectl describe pod` 中出现 `FailedScheduling`。
- Deployment 副本数无法达到期望值。
- 新发布版本无法启动，但旧版本正常。
- 集群节点资源看似充足，但 Pod 无法调度。

## 可能原因

- CPU、Memory、GPU 等资源请求超过节点可用资源。
- 节点存在 taint，但 Pod 未配置对应 toleration。
- Pod 的 nodeSelector、nodeAffinity、podAntiAffinity 约束过严。
- PVC 未绑定或存储类不可用。
- 镜像拉取密钥、命名空间或配额配置异常。
- 集群节点 NotReady 或调度器异常。

## 排查步骤

1. 执行 `kubectl describe pod <pod> -n <namespace>` 查看 Events。
2. 关注 `FailedScheduling` 的详细原因。
3. 检查 Pod 的 requests/limits 是否合理。
4. 执行 `kubectl describe node` 查看节点资源、taints 和状态。
5. 检查 nodeSelector、affinity、tolerations 配置。
6. 如果使用 PVC，检查 `kubectl get pvc` 是否 Bound。
7. 检查 namespace ResourceQuota 和 LimitRange。
8. 查看 kube-scheduler 日志，确认是否存在调度器异常。

## 客户需要提供的信息

- Pod 名称、namespace、集群 ID 和地域。
- `kubectl describe pod` 完整输出。
- Deployment/StatefulSet YAML。
- `kubectl get node -o wide` 和相关节点 describe 输出。
- PVC、StorageClass、ResourceQuota 配置。
- 最近是否调整资源规格、亲和性、污点或存储配置。

## 升级专家/研发的条件

- Events 原因不明确或与实际资源状态不一致。
- 调度器日志显示内部错误。
- 多个 namespace 大面积 Pod Pending。
- 集群控制面组件疑似异常。
