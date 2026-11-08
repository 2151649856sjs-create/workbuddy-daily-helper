# WorkBuddy-Daily 本地辅助工具

给 [L0NE-6/WorkBuddy-Daily](https://github.com/L0NE-6/WorkBuddy-Daily) 补两个小脚本，解决它在本地
（尤其是 Windows 桌面）跑起来的三个麻烦。

不是替代品，是补丁。主脚本还是原项目那个，本项目只放我自己写的外围代码，不含任何第三方代码。

## 解决的三个问题

**1. 短信登录是交互式的，没法自动化**

原项目的 `workbuddy_login.py` 用 `input()` 等验证码，脚本里调不了、定时任务里更不行。
`sms_login_helper.py` 把它拆成两条命令：先发码，再提交，中间可以隔任意长时间。

**2. 默认会杀掉你正在用的 WorkBuddy 客户端**

主脚本的桌面任务分支会执行 `taskkill /F /IM WorkBuddy.exe`，然后用调试端口重新拉起客户端，
目的是抓设备指纹。你要是正在用客户端，这一下就把你干掉了。
`run_local.py` 强制加 `--no-desktop`，彻底跳过这个分支。

代价是拿不到 PC 灵感任务那部分积分。想拿就去掉这个参数，但记得先关掉客户端。

**3. 输出被缓冲，看不到跑到哪了**

原脚本直接跑的时候输出是一次性出来的。`run_local.py` 改成逐行透传，边跑边看，
同时按天写日志到 `logs/YYYY-MM-DD.log`。

## 用法

把两个脚本复制到 WorkBuddy-Daily 目录里，或者在别处运行、用环境变量指过去。

```bash
# Windows
set WORKBUDDY_DAILY_DIR=D:\path\to\WorkBuddy-Daily

# 登录（每个账号一次）
python sms_login_helper.py send   13800000000
python sms_login_helper.py submit 13800000000 123456

# 跑
python run_local.py                  # 全流程
python run_local.py --query          # 只看积分
python run_local.py --tasks checkin  # 只签到
python run_local.py --only 1         # 只跑第 1 个账号
```

多账号就往 `tokens_local.txt` 里一行一个，格式 `手机号:AT:RT`。

## 安全

- 凭据只落在本地 `tokens_local.txt`，不上传、不打印。`.gitignore` 已经屏蔽了它。
- 本项目的脚本不请求任何第三方服务器，只调原项目已有的接口。
- `tokens_local.txt` 里的 `RT`（refresh token）等于账号控制权，泄露了别人能直接操作你的账号。
  别提交、别截图、别发群。
- 想放 GitHub Actions 的话，务必用私有仓库（Import 方式，不要 Fork），
  详见原项目的说明。

## 免责

这些接口来自对客户端的分析，官方更新随时可能失效。仅供个人自动化学习使用，
风险自负。原项目是 MIT 协议，本项目同样。
