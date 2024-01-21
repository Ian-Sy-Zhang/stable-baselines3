Create a new conda environment before running testing_script

```
conda create env -n "SB3Testing" python=3.10
conda activate SB3Testing
```

在提供的 `dqn.py` 文件中，我们可以引入几个不容易被察觉的错误。请注意，这些错误通常不是好的编程实践，而是为了完成您的特定要求。下面是一些可能的错误：

1. **初始化方法中的默认参数错误**：
   将 `tau` 的默认值设置为超出其应有范围的数值，例如 `2.0`，这可能会导致目标网络的更新不正确。

    ```python
    tau: float = 2.0,  # 应在 0 到 1 之间
    ```

2. **梯度裁剪的遗漏**：
   在 `train` 方法中，故意省略 `th.nn.utils.clip_grad_norm_()` 调用，这可能会导致梯度爆炸问题但并不容易被注意到。

    ```python
    # Clip gradient norm
    # th.nn.utils.clip_grad_norm_(self.policy.parameters(), self.max_grad_norm)  # 故意省略
    ```

3. **错误的批量归一化统计更新**：
   在 `_on_step` 方法中，将批量归一化统计信息的更新权重从 `1.0` 改为 `tau`，这是不正确的，因为批量归一化的统计信息应该完全复制，而不是通过 Polyak 更新。

    ```python
    # polyak_update(self.batch_norm_stats, self.batch_norm_stats_target, 1.0)  # 正确的方法
    polyak_update(self.batch_norm_stats, self.batch_norm_stats_target, self.tau)  # 错误的方法
    ```

4. **错误的环境步骤计数**：
   在 `_on_step` 方法中，错误地计算环境步数。例如，如果 `target_update_interval` 是一个小于 `n_envs` 的数值，将永远不会执行 `polyak_update`。

    ```python
    if self._n_calls % max(self.target_update_interval // self.n_envs, 1) == 0:
        # ...
    ```

5. **探索率调度错误**：
   在探索率调度的定义中，错误地交换 `exploration_initial_eps` 和 `exploration_final_eps` 的值，导致探索率的变化与预期相反。

    ```python
    self.exploration_schedule = get_linear_fn(
        self.exploration_final_eps,  # 应该是 self.exploration_initial_eps
        self.exploration_initial_eps,  # 应该是 self.exploration_final_eps
        self.exploration_fraction,
    )
    ```

6. **错误的 `train` 方法中的 `batch_size` 参数**：
   在 `train` 方法的签名中，设置默认的 `batch_size` 参数为一个不常用的数值，如 `100`，而不是类初始化时定义的 `32`。

    ```python
    def train(self, gradient_steps: int, batch_size: int = 100) -> None:  # 应该与初始化中的值一致
    ```

这些错误可能会导致算法性能不佳，以及在某些情况下模型训练失败，但它们不容易直接从代码中发现。在实际应用中，应该避免这些错误，并通过适当的测试和验证来确保代码的质量。