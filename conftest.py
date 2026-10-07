import os
import subprocess
import pytest


# ① 讓執行 pytest 時可以多加一個參數 --image，指定要測哪個版本
#    沒指定的話，預設測 mini-baseos:24.04
def pytest_addoption(parser):
    parser.addoption("--image", default="mini-baseos:24.04", help="Image under test")


# ② 代表「受測機器」，只有一個功能：在它裡面執行一行指令，把結果拿回來
class Target:
    def __init__(self, container):
        self.container = container  # 記住受測 container 的名字

    def run(self, cmd, user=None):
        # 組出指令：docker exec [-u 使用者] 容器名稱 bash -c "要執行的指令"
        docker_cmd = ["docker", "exec"]
        if user:
            docker_cmd += ["-u", user]  # 指定用哪個帳號執行（測權限時用）
        docker_cmd += [self.container, "bash", "-c", cmd]
        # 執行並回傳結果：returncode（成功與否）、stdout（輸出內容）
        return subprocess.run(docker_cmd, capture_output=True, text=True)


# ③ fixture：測試開始前開機、結束後關機
#    scope="session" 代表整輪測試只開一台，所有測試共用
@pytest.fixture(scope="session")
def target(request):
    image = request.config.getoption("--image")  # 讀取 --image 參數

    # 幫受測 container 取一個不會重複的名字，例如 dut-mini-baseos-24-04-12345
    name = f"dut-{image.replace(':', '-').replace('.', '-')}-{os.getpid()}"

    # 開機：用指定的 image 開一個 container，sleep infinity 讓它一直開著等檢查
    subprocess.run(
        ["docker", "run", "-d", "--name", name, image, "sleep", "infinity"],
        check=True, capture_output=True,
    )

    yield Target(name)  # 把受測機器交給測試使用，測試跑完才會繼續往下

    # 關機：刪掉這個 container
    subprocess.run(["docker", "rm", "-f", name], capture_output=True)