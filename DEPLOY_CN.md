# 国内镜像部署说明

判断：国内镜像用于补足 GitHub Pages 访问不稳定的问题，不作为外部候选人材料发送。

## 生成方式

```bash
python3 scripts/build_cn_release.py
```

| 产物 | 用途 |
|---|---|
| `dist-cn/` | 上传到 EdgeOne Pages 的静态站目录 |
| `deliverables/latest/` | 每次对外发送的最新交付目录 |
| `Tim_Zhang_Portfolio_Offline.zip` | 面试前发送的离线包 |
| `Tim_Zhang_Portfolio_Snapshot_CN.pdf` | 中文个人主页网页快照 |
| `Tim_Zhang_Portfolio_Snapshot_EN.pdf` | 英文个人主页网页快照 |
| `Tim_Zhang_Portfolio_Long_Screenshot_CN.png` | 中文个人主页长截图 |
| `Tim_Zhang_Portfolio_Long_Screenshot_EN.png` | 英文个人主页长截图 |

## EdgeOne Pages 上传

### CLI 自动发布

```bash
scripts/deploy_edgeone.sh
```

| 本地配置 | 说明 |
|---|---|
| `.edgeone/.Token` | EdgeOne API Token，本地保存，不提交 |
| `EDGEONE_PROJECT_NAME` | 默认 `tim-portfolio` |
| `EDGEONE_ENVIRONMENT` | 默认 `production` |
| `EDGEONE_AREA` | 默认 `global` |

### 手动上传备用

1. 运行 `python3 scripts/build_cn_release.py`。
2. 打开 EdgeOne Pages 的 Upload 入口。
3. 上传 `dist-cn/` 目录内全部文件。
4. 获得默认访问入口后，作为备用链接。

## 交付习惯

- 每次主页更新后，只运行一次 `python3 scripts/build_cn_release.py`。
- 对外发送 `deliverables/latest/` 中的 PDF 或 ZIP。
- `manifest.json` 会记录生成时间、当前 commit 和文件大小。

## 约束

- 暂无域名时，不走 ICP 备案版正式站。
- `dist-cn/` 会移除 Google Fonts 远程依赖，改用系统字体。
- GitHub 链接保留，但会标注 `Global link / 海外链接`。
