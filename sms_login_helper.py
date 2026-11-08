#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""短信登录辅助工具，把「发验证码」和「提交验证码」拆成两条命令。

为什么需要：原项目的 workbuddy_login.py 是交互式的，用 input() 等验证码，
没法在脚本、定时任务或自动化流程里调用。本工具把流程拆开：

  python sms_login_helper.py send   13800000000
  python sms_login_helper.py submit 13800000000 123456

提交成功后，凭据以「手机号:AT:RT」一行追加到 tokens_local.txt，不回显 token。

依赖：同目录或 WORKBUDDY_DAILY_DIR 下要有 workbuddy_login.py（原项目自带）。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOKENS = os.path.join(HERE, "tokens_local.txt")


def mask(phone):
    return phone[:3] + "****" + phone[-4:] if len(phone) >= 7 else "***"


def resolve_project_dir():
    candidates = [os.environ.get("WORKBUDDY_DAILY_DIR"), HERE]
    for d in candidates:
        if d and os.path.isfile(os.path.join(d, "workbuddy_login.py")):
            return d
    return None


def main():
    if len(sys.argv) < 3:
        print("usage:")
        print("  python sms_login_helper.py send   <phone>")
        print("  python sms_login_helper.py submit <phone> <code>")
        return 2

    project = resolve_project_dir()
    if not project:
        print("找不到 workbuddy_login.py。")
        print("把本脚本放进 WorkBuddy-Daily 目录，或者设置 WORKBUDDY_DAILY_DIR。")
        return 1
    sys.path.insert(0, project)
    import workbuddy_login as wl

    mode = sys.argv[1]
    phone = sys.argv[2].strip()

    if mode == "send":
        ok, msg = wl.send_sms(phone)
        print("SEND_OK %s" % mask(phone) if ok else "SEND_FAIL %s" % msg)
        return 0 if ok else 1

    if mode == "submit":
        if len(sys.argv) < 4:
            print("缺少验证码")
            return 2
        code = sys.argv[3].strip()
        res = wl.login(phone, code)
        if not res:
            print("LOGIN_FAIL")
            return 1
        line = "%s:%s:%s" % (res["phone"], res["accessToken"], res["refreshToken"])
        with open(TOKENS, "a", encoding="utf-8") as f:
            f.write(line + "\n")
        print("LOGIN_OK %s 已保存到 tokens_local.txt" % mask(phone))
        return 0

    print("未知模式: %s" % mode)
    return 2


if __name__ == "__main__":
    sys.exit(main())
