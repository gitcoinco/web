# Token Profile

你可以通过这篇教程了解如何通过 Github 自主提交 token 信息到 imToken，以便于你的 token 信息能在 imToken2.0 APP 里面对应的 token profile 页面显示出来。

该页面位于：
钱包资产首页 -> 对应 Token (以 ETH 为例) -> Token Profile 按钮(页面右上角)。

页面显示如下：

![Wallet Tab](tutorial/sample.png)

*其他语言版本: [English](README.md),[简体中文](README.zh-CN.md).*

## 具体如何操作？

**注意：我们暂时只接受提交 ERC20 代币信息。**
1. Fork 这个 repo 到你的账户
2. 从你自己的账户里面 clone 这个 repo，注意不是直接 clone 最原始的 repo， 而是 clone 你 fork 的那个 repo

```
git clone git@github.com:xxxxxxxx/token-profile.git
```

3. 创建并且切换到用你的 token symbol 命名的分支里
4. 在 erc20 目录里添加一个新的 json 文件，使用 **checksum** 代币合约地址命名这个 json 文件。举例：
*0xf90f1648926005A8bb3ed8ec883164De7F768743.json*

5. json 文件的内容参照模板文件：[$template.json](./erc20/$template.json)
6. 代币 logo 放到 images 目录里，图片名称也是使用 **checksum** 代币合约地址命名。对于 logo 的要求参照下面的说明
7. 如果你的代币已经被添加了，你可以在对应的目录下更新相应的代币信息
8. commit 提交信息
9. push 提交信息到你的 repo
10. 在你的 repo 页面下点击 `New pull request` 按钮，并附上详细的描述（比如建议设置的 gas ，默认为 60000）
11. 我们会尽快核实你的 PR，如果 PR 没问题我们会合并到主分支下

## 要求
### 资料的有效性和准确性
首先你需要对你提交的资料负责，所以务必保证代币信息的准确度，包括 Logo 等。

### Logo 设计要求
- 尺寸: 120x120 像素
- 图片为透明背景的 PNG 格式
- 品牌标识水平竖直居中顶边，见下图

![example](tutorial/logo.png)

## Copyright

2018&copy;imToken PTE. LTD.