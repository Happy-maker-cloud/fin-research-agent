import math

import torch
from torch import nn


def tensor_and_autograd_demo() -> None:
    x = torch.tensor(
        [1.0, 2.0, 3.0],
        requires_grad=True,
    )

    loss = (x**2).sum()
    loss.backward()

    print("x:", x)
    print("loss:", loss.item())
    print("gradient:", x.grad)


class TinyNetwork(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(4, 8),
            nn.ReLU(),
            nn.Linear(8, 2),
        )

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        return self.network(inputs)


def scaled_dot_product_attention(
    query: torch.Tensor,
    key: torch.Tensor,
    value: torch.Tensor,
) -> tuple[torch.Tensor, torch.Tensor]:
    dimension = query.size(-1)

    scores = query @ key.transpose(-2, -1)
    scores = scores / math.sqrt(dimension)

    attention_weights = torch.softmax(
        scores,
        dim=-1,
    )

    output = attention_weights @ value

    return output, attention_weights


def append_kv_cache(
    cached_key: torch.Tensor | None,
    cached_value: torch.Tensor | None,
    new_key: torch.Tensor,
    new_value: torch.Tensor,
) -> tuple[torch.Tensor, torch.Tensor]:
    if cached_key is None or cached_value is None:
        return new_key, new_value

    updated_key = torch.cat(
        [cached_key, new_key],
        dim=-2,
    )
    updated_value = torch.cat(
        [cached_value, new_value],
        dim=-2,
    )

    return updated_key, updated_value


def main() -> None:
    torch.manual_seed(42)

    tensor_and_autograd_demo()

    model = TinyNetwork()
    inputs = torch.randn(3, 4)
    outputs = model(inputs)

    print("network input shape:", inputs.shape)
    print("network output shape:", outputs.shape)

    query = torch.randn(1, 3, 4)
    key = torch.randn(1, 3, 4)
    value = torch.randn(1, 3, 4)

    attention_output, attention_weights = scaled_dot_product_attention(
        query,
        key,
        value,
    )

    print("attention output shape:", attention_output.shape)
    print("attention weights:", attention_weights)

    cached_key = key[:, :2, :]
    cached_value = value[:, :2, :]
    new_key = key[:, 2:, :]
    new_value = value[:, 2:, :]

    updated_key, updated_value = append_kv_cache(
        cached_key,
        cached_value,
        new_key,
        new_value,
    )

    print("cached key shape:", cached_key.shape)
    print("updated key shape:", updated_key.shape)
    print("updated value shape:", updated_value.shape)


if __name__ == "__main__":
    main()
