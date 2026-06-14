"""
No Creeps Were Harmed TD - Unlimited Credits Trainer
Tested: Steam v1.3.3 (buildid 20242545)

Hotkeys:
  F1  - Toggle unlimited credits
  F2  - Set credits once to 99999999
  END - Exit trainer
"""

from __future__ import annotations

import ctypes
import sys
import threading
import time
from ctypes import wintypes

try:
    import keyboard
    import pymem
    import pymem.process
except ImportError:
    print("缺少依赖，请先运行: pip install pymem keyboard")
    sys.exit(1)

PROCESS_NAME = "No Creeps Were Harmed TD"
MODULE_NAME = "GameAssembly.dll"

# Il2CppDumper RVAs for build 20242545 / game v1.3.3
RVA_GET_PLAYER_CASH = 0x245030
RVA_SET_PLAYER_CASH = 0x246E90

TARGET_CREDITS = 99_999_999.0
POLL_INTERVAL = 0.1

kernel32 = ctypes.windll.kernel32


class CashTrainer:
    def __init__(self) -> None:
        self.pm: pymem.Pymem | None = None
        self.base = 0
        self._get_stub = 0
        self._set_stub = 0
        self._result_mem = 0
        self._value_mem = 0
        self.enabled = False
        self.running = True
        self._lock = threading.Lock()

    def attach(self) -> None:
        self.pm = pymem.Pymem(PROCESS_NAME)
        module = pymem.process.module_from_name(self.pm.process_handle, MODULE_NAME)
        self.base = module.lpBaseOfDll
        self._alloc_stubs()
        print("[OK] 已附加到游戏进程")
        print(f"[OK] GameAssembly.dll = 0x{self.base:X}")

    def _alloc_stubs(self) -> None:
        assert self.pm is not None
        get_cash = self.base + RVA_GET_PLAYER_CASH
        set_cash = self.base + RVA_SET_PLAYER_CASH

        self._result_mem = self.pm.allocate(16)
        self._value_mem = self.pm.allocate(16)

        get_stub = (
            b"\x48\x83\xEC\x28"
            + b"\x48\xB8" + get_cash.to_bytes(8, "little")
            + b"\xFF\xD0"
            + b"\x48\xBB" + self._result_mem.to_bytes(8, "little")
            + b"\xF3\x0F\x11\x03"
            + b"\x48\x83\xC4\x28\xC3"
        )

        set_stub = (
            b"\x48\xB8" + self._value_mem.to_bytes(8, "little")
            + b"\xF3\x0F\x10\x00"
            + b"\x48\x83\xEC\x28"
            + b"\x48\xB8" + set_cash.to_bytes(8, "little")
            + b"\xFF\xD0"
            + b"\x48\x83\xC4\x28\xC3"
        )

        self._get_stub = self.pm.allocate(len(get_stub) + 64)
        self._set_stub = self.pm.allocate(len(set_stub) + 64)
        self.pm.write_bytes(self._get_stub, get_stub, len(get_stub))
        self.pm.write_bytes(self._set_stub, set_stub, len(set_stub))

    def _run_remote(self, address: int) -> None:
        assert self.pm is not None
        thread_id = wintypes.DWORD()
        handle = kernel32.CreateRemoteThread(
            ctypes.c_void_p(self.pm.process_handle),
            None,
            0,
            ctypes.c_void_p(address),
            None,
            0,
            ctypes.byref(thread_id),
        )
        if not handle:
            raise RuntimeError(f"CreateRemoteThread 失败: {ctypes.get_last_error()}")
        kernel32.WaitForSingleObject(handle, 5000)
        kernel32.CloseHandle(handle)

    def get_credits(self) -> float:
        with self._lock:
            self._run_remote(self._get_stub)
            assert self.pm is not None
            return self.pm.read_float(self._result_mem)

    def set_credits(self, value: float) -> None:
        with self._lock:
            assert self.pm is not None
            self.pm.write_float(self._value_mem, float(value))
            self._run_remote(self._set_stub)

    def apply_unlimited(self) -> None:
        current = self.get_credits()
        if abs(current - TARGET_CREDITS) > 0.5:
            self.set_credits(TARGET_CREDITS)

    def worker(self) -> None:
        while self.running:
            if self.enabled:
                try:
                    self.apply_unlimited()
                except Exception as exc:
                    print(f"[错误] {exc}")
                    self.enabled = False
            time.sleep(POLL_INTERVAL)

    def toggle(self) -> None:
        self.enabled = not self.enabled
        state = "开启" if self.enabled else "关闭"
        try:
            credits = self.get_credits()
            print(f"[状态] 无限信用点: {state} | 当前信用点: {credits:.0f}")
            if self.enabled:
                self.apply_unlimited()
                print(f"[完成] 信用点已设为 {TARGET_CREDITS:.0f}")
        except Exception as exc:
            print(f"[错误] {exc}")
            self.enabled = False

    def set_once(self) -> None:
        try:
            self.set_credits(TARGET_CREDITS)
            print(f"[完成] 信用点已设为 {TARGET_CREDITS:.0f}")
        except Exception as exc:
            print(f"[错误] {exc}")


def is_admin() -> bool:
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def main() -> None:
    if not is_admin():
        print("[警告] 未以管理员身份运行，附加进程可能失败。")
        print("       请右键以管理员身份运行。")

    print("=" * 52)
    print(" NCWHTD 无限信用点修改器")
    print("=" * 52)
    print("1. 先启动游戏并进入地图（对局中）")
    print("2. 以管理员身份运行本程序")
    print("3. F1 = 开关无限信用点 (锁定 99999999)")
    print("4. F2 = 一次性设为 99999999")
    print("5. END = 退出")
    print("=" * 52)

    trainer = CashTrainer()

    while True:
        try:
            trainer.attach()
            break
        except pymem.exception.ProcessNotFound:
            print("[等待] 未找到游戏，请先启动游戏后按 Enter...")
            input()
        except Exception as exc:
            print(f"[错误] 附加失败: {exc}")
            print("按 Enter 重试...")
            input()

    try:
        credits = trainer.get_credits()
        print(f"[OK] 当前信用点: {credits:.0f}")
    except Exception as exc:
        print(f"[警告] 暂时无法读取信用点: {exc}")
        print("[提示] 请先进入地图对局，再按 F1。")

    threading.Thread(target=trainer.worker, daemon=True).start()

    keyboard.add_hotkey("f1", trainer.toggle)
    keyboard.add_hotkey("f2", trainer.set_once)
    keyboard.wait("end")

    trainer.running = False
    print("[退出] 修改器已关闭。")


if __name__ == "__main__":
    main()
