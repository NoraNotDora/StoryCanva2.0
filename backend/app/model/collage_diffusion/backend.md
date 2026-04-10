# 算法 1: Collage Diffusion 生成算法

**输入**: 
- 完整图像描述文本 $c$ (如："A bento box with rice, edamame, ginger, and sushi")
- 图层序列 $L = \{l_1, l_2, ..., l_n\}$，从后向前排序，每个图层 $l_i$ 包含:
  - RGBA图像 $x_i$ 及其alpha通道 $x_i^\alpha$
  - 图层描述文本 $c_i$ (是 $c$ 的子字符串)
  - 图层位置、旋转和缩放参数 $p_i, r_i, s_i$
  - CAC强度参数 $\lambda_i$ 和负向强度参数 $\lambda_i^{neg}$
  - 噪声强度参数 $\eta_i$
  - 边缘检测强度参数 $\kappa_i$
- 扩散步数 $T$，引导缩放参数 $\omega$

**输出**: 生成的拼贴图像 $I$

1: 提取各图层参数 $\lambda = [\lambda_1,...,\lambda_n]$, $\lambda^{neg} = [\lambda_1^{neg},...,\lambda_n^{neg}]$, $\kappa = [\kappa_1,...,\kappa_n]$, $\eta = [\eta_1,...,\eta_n]$
2: $I_{comp}, M = \text{合并图层}(L)$ // 创建复合图像和遮罩层
3: $M_{pyr} = [\text{创建遮罩金字塔}(m_i)$ for $m_i \in M]$ // 多尺度遮罩
4: // 处理文本标记和注意力控制
5: $\tau = \emptyset$, $\mu = \emptyset$, $\lambda_{all} = \emptyset$, $\lambda^{neg}_{all} = \emptyset$ 
6: **for** 每个图层 $l_i \in L$ **do**
7:   $tok_i = \text{分词}(c_i)$
8:   $pos_i = \text{在}c\text{中查找}c_i\text{的token位置}$
9:   **for** 每个匹配的token位置 $p \in pos_i$ **do**
10:    $\tau.\text{添加}(p)$
11:    $\mu.\text{添加}(M_{pyr}[i])$
12:    $\lambda_{all}.\text{添加}(\lambda_i)$
13:    $\lambda^{neg}_{all}.\text{添加}(\lambda_i^{neg})$
14:  **end for**
15: **end for**
16: // 创建注意力修改函数
17: $A(u, \sigma) = \text{初始化注意力控制}(u, \tau, \mu, \lambda_{all}, \lambda^{neg}_{all}, \sigma)$
18: // 准备控制遮罩
19: $M_{canny} = \text{生成边缘控制遮罩}(M, \kappa)$
20: $\eta_{max} = \max(\eta)$ // 最大噪声强度作为整体强度
21: $M_{noise} = \text{生成噪声遮罩}(M, \eta_{max}, \eta)$
22: // 准备扩散过程
23: $z = \text{编码图像}(I_{comp})$ // 初始潜变量
24: $z_0 = z$ // 保存初始状态
25: $t_{seq} = \text{计算时间步序列}(T, \eta_{max})$
26: // 扩散迭代
27: **for** $t \in t_{seq}$ **do**
28:   $\sigma = \text{计算噪声等级}(t)$
29:   $A(unet, \sigma)$ // 修改UNet中的注意力机制
30:   // 应用ControlNet条件
31:   $res_{down}, res_{mid} = \text{ControlNet}(z, t, c, M_{canny})$
32:   // UNet推理
33:   $\epsilon = \text{UNet}(z, t, c, res_{down}, res_{mid})$
34:   $z = \text{去噪一步}(\epsilon, t, z)$
35:   // 应用遮罩引导
36:   $noise = \text{生成随机噪声}(z.\text{shape})$
37:   $z_{noised} = \text{向}z_0\text{添加噪声}(noise, t)$
38:   $M_t = (M_{noise} > (1-t/1000)).\text{类型}(M_{noise}.\text{dtype})$
39:   $d = \lfloor 4 \times t/1000 \rfloor$ // 膨胀大小
40:   $M_t^{dilated} = \text{膨胀}(M_t, d)$
41:   $z = z_{noised} \times M_t^{dilated} + z \times (1 - M_t^{dilated})$
42: **end for**
43: $I = \text{解码潜变量}(z)$
44: **return** $I$

## 子算法: 初始化注意力控制

**输入**: 
- UNet模型 $u$
- token位置列表 $\tau$
- 遮罩金字塔列表 $\mu$
- 强度参数列表 $\lambda$
- 负向强度参数列表 $\lambda^{neg}$
- 当前噪声等级 $\sigma$

**输出**: 修改后的UNet模型

1: **for** 每个(名称, 模块) in $u$.命名模块() **do**
2:   **if** 模块类型 = "Attention" 且 "attn2" in 名称 **then**
3:     // 替换注意力处理器
4:     定义 $\text{处理器}(\text{self}, \text{attn}, hs, enc\_hs=None, attn\_mask=None)$:
5:       // 标准注意力计算
6:       $q = \text{attn.to\_q}(hs)$
7:       $k = \text{attn.to\_k}(enc\_hs)$ 
8:       $v = \text{attn.to\_v}(enc\_hs)$
9:       
10:      // 格式转换和计算注意力分数
11:      $q, k, v = \text{转换格式}(q, k, v)$
12:      $scores = \text{计算注意力分数}(q, k)$
13:      
14:      // 注意力修改 (CAC算法核心)
15:      $scores = \text{应用空间修改}(scores, \tau, \mu, \lambda, \lambda^{neg}, \sigma)$
16:      
17:      // 完成注意力计算
18:      $probs = \text{softmax}(scores)$
19:      $output = \text{bmm}(probs, v)$
20:      $output = \text{attn.to\_out}(output)$
21:      **return** $output$
22:    
23:    模块.处理器 = 处理器
24:  **end if**  
25: **end for**
26: **return** $u$
