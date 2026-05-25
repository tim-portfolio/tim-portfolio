# 国内镜像部署说明

判断：国内镜像用于补足 GitHub Pages 访问不稳定的问题，不作为外部候选人材料发送。

## 生成方式

```bash
python3 scripts/build_cn_release.py
```

| 产物 | 用途 |
|---|---|
| `dist-cn/` | 上传到 EdgeOne Pages 的静态站目录 |
| `Tim_Zhang_Portfolio_Offline.zip` | 面试前发送的离线包 |
| `Tim_Zhang_Portfolio_Snapshot.pdf` | 个人主页网页快照 |
| `Tim_Zhang_Portfolio_Long_Screenshot.png` | 个人主页长截图 |

## EdgeOne Pages 上传

1. 运行生成脚本。
2. 打开 EdgeOne Pages 的 Upload 入口。
3. 上传 `dist-cn/` 目录内全部文件。
4. 获得默认访问入口后，作为 GitHub Pages 的备用链接。

## 约束

- 暂无域名时，不走 ICP 备案版正式站。
- `dist-cn/` 会移除 Google Fonts 远程依赖，改用系统字体。
- GitHub 链接保留，但会标注 `Global link / 海外链接`。
