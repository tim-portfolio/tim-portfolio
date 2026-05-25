# GitHub Pages 国内访问兜底包

判断：本项目采用“GitHub Pages 主站 + 国内镜像 + 离线分享包”。

## 生成方式

在仓库根目录运行：

```bash
python3 scripts/build_cn_release.py
```

生成结果：

| 产物 | 用途 |
|---|---|
| `dist-cn/` | 上传到 EdgeOne Pages 的静态站目录 |
| `Tim_Zhang_Portfolio_Offline.zip` | 微信、邮件、面试前发送的离线包 |
| `Tim_Zhang_Portfolio_Snapshot.pdf` | 网页打不开时直接查看的 PDF 快照 |

## EdgeOne Pages 上传方式

1. 运行生成脚本。
2. 打开 EdgeOne Pages 的 Upload 入口。
3. 上传 `dist-cn/` 目录内的全部文件。
4. 获得默认访问入口后，把它作为 GitHub Pages 的国内备用链接。

## 离线包使用方式

1. 发送 `Tim_Zhang_Portfolio_Offline.zip`。
2. 对方解压后直接打开 `index.html`。
3. 如果网页环境不方便打开，就看 `Tim_Zhang_Portfolio_Snapshot.pdf`。

## 设计约束

- 不需要域名和 ICP 备案。
- `dist-cn/` 会移除 Google Fonts 远程依赖，改用系统字体。
- GitHub 链接会保留，但标注为 `Global link / 海外链接`。
- 页面主体内容、图片、视频、简历 PDF 都会随包复制，避免依赖 GitHub 才能展示。
