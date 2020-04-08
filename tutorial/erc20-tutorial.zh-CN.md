# ERC20 Token Profile 提交教程

*查看 [Token Profile 指南](../README.zh-CN.md)*

## 要求
### 资料准备
#### 完善的项目资料以及相关区块链媒体报道，包括但不限于以下：

- 官方公告：（**[资料的完整和准确](https://github.com/consenlabs/token-profile/blob/master/tutorial/erc20-tutorial.zh-CN.md#%E8%B5%84%E6%96%99%E7%9A%84%E5%AE%8C%E6%95%B4%E5%92%8C%E5%87%86%E7%A1%AE)** 中会详细说明）
- 团队背景：
- 项目基本情况：
- 媒体报道：
- 收录的交易所：
- 代币转账调用智能合约需要的 Gas limit（默认值 60000）


#### Token Profile 提交：
参考模版：https://github.com/consenlabs/token-profile/pull/1636/files

### 对资料的要求
#### 资料的完整和准确
你需要对提交的资料负责，务必保证所提资料真实有效。参考示例模版，完善的资料有助于 imToken 团队更了解你们的项目，加速显示进度。

为确保资料提交的真实性，请在贵方官网或其他经过认证的社交媒体渠道发布公告，并将此公告链接附于「官方公告」。推荐文案：
>\#imToken# #1636#
我们正在完善 XXX 在 imToken 中的代币相关资料。完成后，大家可以在 imToken 里看到 logo，更方便地管理 XXX，同时能看到更多代币信息。

注：
- 1636 为 pr 序号，如 https://github.com/consenlabs/token-profile/pull/1636 的序号为 1636，这是帮助 imToken **判断 pr 真实性的关键**。
- #imToken #1636 标签及其展示形式可自行调整。
- 若未提供「官方公告」，则无法显示代币信息。

#### Logo 设计要求
- 尺寸: 120x120 像素
- 图片为透明背景的 PNG 格式
- 品牌标识水平竖直居中顶边，见下图

![example](./logo.png)

## 具体如何操作？
*建议由技术人员协助完成*

1. Fork 这个仓库到你的账户
2. 克隆到本地，注意：不是直接克隆最原始的仓库，而是克隆你 fork 的那个仓库

```
git clone git@github.com:xxxxxxxx/token-profile.git
cd token-profile/
```

3. 创建并且切换到用你的 token symbol 命名的分支里
 举例：
```
git branch xxx-token
git checkout xxx-token
```

4. 在 erc20 目录里添加一个新的 json 文件，使用你的代币合约地址命名这个文件，注意合约地址需要有大小写做了 [checksum](https://github.com/ethereum/EIPs/blob/master/EIPS/eip-55.md)
 举例：
 *0xf90f1648926005A8bb3ed8ec883164De7F768743.json* [Checksum 转化工具](https://ethsum.netlify.com/)

5. json 文件请使用 UTF-8 编码，否则 Travis-CI 会构建失败。json中的合约地址也需要使用**checksum**。请参照模版文件补充完整的代币资料：[$template.json](../erc20/$template.json)
   
6. 代币 Logo 放到 images 目录里，图片名称也是使用 **checksum** 代币合约地址命名
   
7. Commit 并且 Push 提交信息到你的仓库
 举例：
```
git add -A
git commit -m “Add xxx token”
git push origin xxx-token
```

8. 在你的仓库页面下点击 `New pull request` 按钮 ，并附上项目资料、官方公告以及相关区块链媒体报道，包括但不限于以下：（官方公告；团队背景；项目基本情况；媒体报道；收录的交易所；代币转账调用智能合约需要的 Gas limit）


PR 示例：https://github.com/consenlabs/token-profile/pull/1636 

9. 我们会尽快核实你的 PR，如果 PR 没问题我们会合并到主分支下，至此你的代币资料将会出现在 imToken App 内

## 常见问题

### 如何显示价格？
imToken 目前的价格显示对接 block.cc 的 API，如需在 imToken 中显示价格，你们的代币要求被 block.cc 收录；并在 GitHub Issues 提供相关资料，提交示例模版：
https://github.com/consenlabs/token-profile/issues/3565 


### 关于重名及修改合约

在 imToken 1.0 里，如果你的项目名称和其它项目重复，我们会在后面加数字，如 TFT1、TFT2、TFT3 等；如果你希望去掉数字，我们首先声明，这是一个非常危险的操作，修改代币信息后，代币会突然消失，容易引起用户恐慌，原则是对于持币人数多的项目，我们建议项目方推荐用户下载使用 imToken 2.0，imToken 2.0 通过代币合约地址来区分代币，所以不存在代币名称重复。

如需修改合约地址，需要项目方在社区发布修改合约公告。并在 GitHub 提交新的 PR，将旧合约 Logo 作去色处理（Photoshop 操作路径：图像 - 调整 - 去色），然后提交新的代币合约和 Logo，并把公告链接在 PR 下留言，我们会核实情况修改。

### 无法通过合约搜索
通过合约地址搜索不出来的情况，请查看是否是并未有成功的转账记录，另外请在 [Etherscan](https://etherscan.io/) verify 你的合约信息，我们可以帮你手动添加。

## Copyright

2020&copy;imToken PTE. LTD.
