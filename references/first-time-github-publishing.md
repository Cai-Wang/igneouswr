# 首次 GitHub 发布流程（给零基础用户）

用户特征：完全没有接触过 Git/GitHub，听到 `gh`、`SSH`、`remote` 等术语会困惑。
指令原则：**只说浏览器操作步骤**，不说终端命令。每步完成后让用户确认。

## 场景：本地已有 git 仓库，需要发布到 GitHub

### 第1步：用户去 GitHub 网页创建空仓库

1. 用户打开 https://github.com （已登录）
2. 点页面右上角绿色 **New** 按钮 或进 https://github.com/new
3. Repository name 填：`igneouswr`
4. **Public** 选中（公开）
5. **不要勾** "Add a README" / ".gitignore" / "license"（全部不选）
6. 点底部绿色 **Create repository**

### 第2步：用户复制 remote 命令

创建成功后页面跳转，显示几行命令。让用户复制以 `git remote add` 开头的那段（约 3 行）贴给 agent。

### 第3步：如果 push 报 "could not read Username"

因为 WSL 终端非交互，HTTPS 无法输密码。解决：

1. 在 WSL 生成 SSH 密钥：

```bash
ssh-keygen -t ed25519 -C "user@email.com" -f ~/.ssh/id_ed25519 -N ""
```

2. 让用户打开 https://github.com/settings/keys
3. 点 **New SSH key**
4. Title 填描述性名称（如 `WSL Hermes`），Key 框粘贴 `cat ~/.ssh/id_ed25519.pub` 的输出
5. 点 **Add SSH key**
6. 改 remote 为 SSH 格式：

```bash
git remote set-url origin git@github.com:用户名/仓库名.git
```

7. 如果报 "Host key verification failed"，先执行：

```bash
ssh-keyscan github.com >> ~/.ssh/known_hosts
```

8. 然后 `git push -u origin main`

### 第4步：验证

让用户打开 `https://github.com/用户名/仓库名` 确认项目已可见。

## 后续日常修改

用户只需告诉 agent "改了什么" → agent 执行 `git add + commit + push` 并告知"已推上去"。

用户不需要学任何 git 命令。但应养成习惯：每次改完后问一句"推上去了吗"。

## pitfall: 不要假设术语已知

- 不要说 "ssh-keygen"、"gh cli"、"remote"、"upstream" 等术语
- 要说话：**"打开这个网页 → 点这个按钮 → 粘这段内容"**
- 用户说"你在说什么，我不懂 第一次做" → 立即切换到纯浏览器操作指南
