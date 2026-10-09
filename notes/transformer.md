# PyTorch与Transformer学习笔记

## 1. Tensor

Tensor是PyTorch中的多维数组，可在CPU或GPU上执行运算。

## 2. 自动求导

requires_grad=True表示PyTorch需要记录运算过程。
调用loss.backward()后，可以从参数的grad属性读取梯度。

## 3. nn.Module

nn.Module是PyTorch模型的基础类。
模型结构写在__init__中，数据流写在forward中。

## 4. Attention

Attention公式：

Attention(Q,K,V) = softmax(QK^T / sqrt(d_k))V

Q表示查询，K表示匹配依据，V表示需要提取的信息。

## 5. Transformer

Transformer主要由多头注意力、前馈网络、残差连接和
LayerNorm组成。

## 6. KV Cache

KV Cache保存历史Token的Key和Value。
生成新Token时只计算新增部分，减少重复计算。
优点是降低推理计算量，缺点是增加显存占用。