import re
import pytest


# 規格 1：作業系統是 Ubuntu 22.04 或 24.04
def test_os_is_supported_ubuntu(target):
    out = target.run("cat /etc/os-release").stdout   # 讀系統資訊檔
    assert "ID=ubuntu" in out                         # 必須是 Ubuntu
    version = re.search(r'VERSION_ID="([\d.]+)"', out).group(1)  # 抓出版本號
    assert version in ("22.04", "24.04")              # 必須是支援的版本


# 規格 2：Python 版本至少 3.10
def test_python_version_at_least_3_10(target):
    r = target.run("python3 -c 'import sys; print(sys.version_info[0], sys.version_info[1])'")
    assert r.returncode == 0                  # python3 要能執行
    major, minor = map(int, r.stdout.split()) # 例如 "3 12" → 3, 12
    assert (major, minor) >= (3, 10)


# 規格 3：必要工具都有裝（git、curl 各算一個測試）
@pytest.mark.parametrize("tool", ["git", "curl"])
def test_required_tool_installed(target, tool):
    r = target.run(f"command -v {tool}")      # 找得到這個指令就代表有裝
    assert r.returncode == 0, f"{tool} is not installed"


# 規格 4：密碼檔 /etc/shadow 不能讓「其他人」讀寫
def test_shadow_not_readable_by_others(target):
    r = target.run("stat -c %a /etc/shadow")
    perm = int(r.stdout.strip(), 8)
    assert perm & 0o007 == 0, f"/etc/shadow permission is {oct(perm)}, others can access it"


# 規格 4（反向檢查）：用一般帳號去讀密碼檔，必須讀不到
def test_shadow_not_readable_by_service_user(target):
    r = target.run("cat /etc/shadow > /dev/null", user="svc-app")
    assert r.returncode != 0, "svc-app can read /etc/shadow"

# 規格 5：服務帳號存在，而且不是 root
def test_service_account_exists_and_not_root(target):
    r = target.run("id -u svc-app")           # 查帳號的 ID
    assert r.returncode == 0                  # 帳號要存在
    assert int(r.stdout.strip()) != 0         # root 的 ID 是 0，不能是 0


# 規格 6：時區是台北
def test_timezone_is_taipei(target):
    r = target.run("cat /etc/timezone")
    assert r.stdout.strip() == "Asia/Taipei"