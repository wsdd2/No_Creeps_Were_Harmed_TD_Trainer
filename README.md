# No Creeps Were Harmed TD — 无限信用点修改器

网上修改器都要钱，用 Cursor 搓了一个免费的单机信用点（Credits）修改器。

适用于 Steam 版 **No Creeps Were Harmed TD**（测试版本：**v1.3.3**，buildid `20242545`）。

## 功能

- **F1**：开关无限信用点（锁定 `99999999`，消费后自动恢复）
- **F2**：一次性将信用点设为 `99999999`
- **END**：退出修改器

## 使用方法

### 方式一：Python 运行（推荐）

1. 安装 [Python 3.10+](https://www.python.org/downloads/)
2. 双击 `install_dependencies.bat` 安装依赖
3. 启动游戏并**进入地图对局**（能看到顶部「信用点」）
4. **以管理员身份**运行 `run_trainer_python.bat`
5. 在游戏中按 **F1** 开启无限信用点

### 方式二：自行打包 exe

```bat
pip install -r requirements.txt pyinstaller
pyinstaller NCWHTD_Credits_Trainer.spec
```

生成的 exe 位于 `dist\NCWHTD_Credits_Trainer.exe`。

> **Anaconda 用户注意**：若 exe 启动报 `_ctypes` / `ffi.dll` 错误，`NCWHTD_Credits_Trainer.spec` 已尝试自动打包 `ffi.dll`；也可直接使用 Python 方式运行。

打包完成后，可用 `run_trainer_admin.bat` 以管理员身份启动 exe。

## 系统要求

- Windows 10 / 11 64 位
- 需**管理员权限**（读写游戏进程内存）
- 游戏进程名：`No Creeps Were Harmed TD`

## 免责声明

- 本工具仅供**单机娱乐**使用
- 联机模式使用可能违反游戏规则并导致封号
- 杀毒软件可能误报（修改器类工具常见），请自行判断
- 游戏大版本更新后可能需要更新内存偏移（见 `ncwhtd_credits_trainer.py` 中的 `RVA_*` 常量）

## 技术说明

通过 Il2CppDumper 分析 `GameAssembly.dll`，调用游戏内 `Gameplay.SetPlayerCash` / `GetPlayerCash` 实现，无需 CheatHappens 会员。

## License

[MIT](LICENSE)
