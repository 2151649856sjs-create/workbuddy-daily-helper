#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""WorkBuddy-Daily 本地包装器。

做三件事：
  1. 从 tokens_local.txt 读多账号凭据，注入 WORKBUDDY_REFRESH_TOKEN
  2. 强制加 --no-desktop，避免主脚本 taskkill WorkBuddy.exe
  3. 实时输出 + 按天写日志到 logs/

用法：
  python run_local.py              # 全流程签到
  python run_local.py --query      # 只看积分，不签到
  python run_local.py --only 1     # 只跑第 1 个账号
  python run_local.py --tasks checkin   # 只签到，不跑成长任务

原项目目录默认取脚本同级；也可以用环境变量指定：
  set WORKBUDDY_DAILY_DIR=D:\\path\\to\\WorkBuddy-Daily
"""
import datetime
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOKENS = os.path.join(HERE, "tokens_local.txt")
LOG_DIR = os.path.join(HERE, "logs")

FORCE_ARGS = ["--no-desktop"]


def resolve_project_dir():
    """找 workbuddy_daily.py 所在目录。"""
    candidates = [os.environ.get("WORKBUDDY_DAILY_DIR"), HERE]
    for d in candidates:
        if d and os.path.isfile(os.path.join(d, "workbuddy_daily.py")):
            return d
    return None


def load_tokens():
    if not os.path.exists(TOKENS):
        return ""
    lines = []
    with open(TOKENS, encoding="utf-8") as f:
        for ln in f:
            ln = ln.strip()
            if ln and not ln.startswith("#"):
                lines.append(ln)
    return "\n".join(lines)


def main():
    project = resolve_project_dir()
    if not project:
        print("找不到 workbuddy_daily.py。")
        print("把本脚本放进 WorkBuddy-Daily 目录，或者设置环境变量：")
        print("  set WORKBUDDY_DAILY_DIR=D:\\path\\to\\WorkBuddy-Daily")
        return 1

    blocks = load_tokens()
    if not blocks:
        print("tokens_local.txt 里没有凭据。先跑：python workbuddy_login.py")
        print("或者用 sms_login_helper.py 分两步登录。")
        return 1

    env = os.environ.copy()
    env["WORKBUDDY_REFRESH_TOKEN"] = blocks
    env["PYTHONIOENCODING"] = "utf-8"

    args = [sys.executable, os.path.join(project, "workbuddy_daily.py")]
    args += FORCE_ARGS + sys.argv[1:]

    os.makedirs(LOG_DIR, exist_ok=True)
    log_path = os.path.join(LOG_DIR, datetime.date.today().isoformat() + ".log")

    print("账号数: %d" % len(blocks.split("\n")))
    print("原项目: %s" % project)
    print("日志  : %s" % log_path)

    with open(log_path, "a", encoding="utf-8") as f:
        f.write("\n===== %s =====\n" % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        f.flush()
        proc = subprocess.Popen(
            args,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
            cwd=project,
        )
        for line in proc.stdout:
            sys.stdout.write(line)
            sys.stdout.flush()
            f.write(line)
            f.flush()
        proc.wait()
    return proc.returncode


if __name__ == "__main__":
    sys.exit(main())
