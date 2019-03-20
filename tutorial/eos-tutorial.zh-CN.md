# EOS Token Profile 提交教程

*查看 [Token Profile 指南](../README.zh-CN.md)*

## 要求
### 资料准备
#### 完善的项目资料以及相关区块链媒体报道，包括但不限于以下：

- 团队背景：
- 项目基本情况：
- 媒体报道：
- 收录的交易所：


#### Token Profile 提交：
参考模版：https://github.com/consenlabs/token-profile/pull/3475/files

### 对资料的要求
#### 资料的完整和准确
你需要对提交的资料负责，务必保证所提资料真实有效。参考示例模版，完善的资料有助于 imToken 团队更了解你们的项目，加速显示进度。

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
4. 在 eos-token 目录里添加一个新的 json 文件，使用 **symbol@accoutname** 命名这个 json 文件。举例：
  *PUB@publytoken11.json*

5. json 文件请使用 UTF-8 编码，否则 Travis-CI 会构建失败。请参照模版文件补充完整的代币资料：[$template.json](../eos-token/$template.json)
6. 代币 Logo 放到 images 目录里，图片名称也是使用 **symbol@accoutname** 命名
7. Commit 并且 Push 提交信息到你的仓库
  举例：
```
git add -A
git commit -m “Add xxx token”
git push origin xxx-token
```

8. 在你的仓库页面下点击 `New pull request` 按钮 ，并附上项目资料以及相关区块链媒体报道，包括但不限于以下：（团队背景；项目基本情况；媒体报道；收录的交易所）

   PR 示例：https://github.com/consenlabs/token-profile/pull/3475

9. 我们会尽快核实你的 PR，如果 PR 没问题我们会合并到主分支下，至此你的代币资料将会出现在 imToken App 内

## 常见问题

### 如何显示价格？
imToken 目前的价格显示对接 block.cc 的 API，如需在 imToken 中显示价格，你们的代币要求被 block.cc 收录；并提供我们相应的链接，参考：https://mifengcha.com/q/eos 

## 相关
* [EOSPark](https://github.com/BlockABC/eos-tokens)

## Copyright

2018&copy;imToken PTE. LTD.