# Startup Sim — 常见问题排查

按 ❌ 症状 → ✅ 解决方法 格式整理。

---

## 环境安装

### ❌ 症状：`python` 命令找不到

```
'python' 不是内部或外部命令
```

✅ 解决方法：
1. 去 [python.org](https://python.org) 下载 Python 3.9 或更高版本
2. 安装时勾选 "Add Python to PATH"
3. 重新打开终端，再试 `python --version`

### ❌ 症状：Python 版本太低

```
Python 3.8.x
```

✅ 解决方法：
1. 去 [python.org](https://python.org) 下载 Python 3.9+
2. 安装后重新打开终端

### ❌ 症状：`pip install -r requirements.txt` 失败

```
ERROR: Could not find a version that satisfies the requirement
```

✅ 解决方法：
1. 确认 Python 版本 ≥3.9：`python --version`
2. 升级 pip：`python -m pip install --upgrade pip`
3. 如果在公司网络：可能需要配置 pip 镜像源
4. 如果某个包报错：`pip install <包名>` 单独安装试试

### ❌ 症状：venv 创建失败

```
Error: Unable to create virtual environment
```

✅ 解决方法：
1. 确认 Python 安装完整：`python -m ensurepip --default-pip`
2. Windows 用 PowerShell 管理员模式再试
3. 也可以不用 venv，直接用系统 Python（项目不强制 venv）

---

## 游戏启动

### ❌ 症状：`python app.py new --name "xxx"` 报错

```
ModuleNotFoundError: No module named 'xxx'
```

✅ 解决方法：
1. 确认已安装依赖：`pip install -r requirements.txt`
2. 确认当前在 `D:\Startup-sim` 目录下
3. 如果在其他目录：先 `cd D:\Startup-sim`

### ❌ 症状：路径错误，找不到项目目录

```
No such file or directory: 'D:\Startup-sim'
```

✅ 解决方法：
1. 确认项目克隆/下载到了正确位置
2. Windows 用 PowerShell，别用 Git Bash 里的 Unix 路径
3. 可以直接拖拽文件夹到终端获取完整路径

### ❌ 症状：游戏启动后马上退出

✅ 解决方法：
1. 输入 `status` 看看当前状态
2. 输入 `help` 查看命令说明
3. 不要直接按回车，输入文字指令

---

## 开发工具

### ❌ 症状：`make` 命令找不到

```
make: command not found
```

✅ 解决方法：
1. `make` 是开发者工具，普通试玩不需要它
2. 如果需要运行检查，可以手动执行 Makefile 里的命令
3. Windows 用户：`make` 不是系统自带，开发者可以装 `chocolatey install make` 或直接用 WSL

### ❌ 症状：`pytest` 运行失败

```
ERROR: file not found: tests/
```

✅ 解决方法：
1. 确认当前在 `D:\Startup-sim` 目录下
2. 确认 pytest 已安装：`pip install pytest`
3. 确认没有改动测试文件

### ❌ 症状：`playtest.py` 报错

```
ImportError: ...
```

✅ 解决方法：
1. 确认在项目根目录运行：`python scripts/playtest.py`
2. 不要 `cd scripts` 后再运行

### ❌ 症状：`docs-check` 失败

✅ 解决方法：
1. 检查是否修改了 `README.md`、`REPORTS.md`、`VERSION` 等文档文件
2. 检查 `VERSION` 和 `README.md` 标题版本号是否一致
3. 运行 `python scripts/check_docs_consistency.py` 查看详细报错

---

## Git 问题

### ❌ 症状：`git push` 被拒绝

```
! [rejected] master -> master (fetch first)
```

✅ 解决方法：
1. 先拉取最新代码：`git pull origin master`
2. 解决冲突后再 push

### ❌ 症状：`git commit` 后文件没提交上去

✅ 解决方法：
1. 确认先 `git add <文件名>` 添加到暂存区
2. `git status` 查看文件状态
3. 新文件必须 add，修改的文件也要 add
