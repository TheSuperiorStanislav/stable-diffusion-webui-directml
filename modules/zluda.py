import platform
import torch
from torch._prims_common import DeviceLikeType
from modules import shared, devices


conv2d = torch.nn.functional.conv2d
def conv2d_cudnn_disabled(*args, **kwargs):
    torch.backends.cudnn.enabled = False
    R = conv2d(*args, **kwargs)
    torch.backends.cudnn.enabled = True
    return R


def is_zluda(device: DeviceLikeType):
    device = torch.device(device)
    return torch.cuda.get_device_name(device).endswith("[ZLUDA]")


def test(device: DeviceLikeType):
    device = torch.device(device)
    try:
        ten1 = torch.randn((2, 4,), device=device)
        ten2 = torch.randn((4, 8,), device=device)
        out = torch.mm(ten1, ten2)
        return out.sum().is_nonzero()
    except Exception:
        return False


def initialize_zluda():
    device = devices.get_optimal_device()
    if platform.system() == "Windows" and torch.cuda.is_available() and is_zluda(device):
        torch.backends.cudnn.enabled = shared.cmd_opts.use_zluda_dnn
        torch.backends.cuda.enable_flash_sdp(False)
        torch.backends.cuda.enable_math_sdp(True)
        torch.backends.cuda.enable_mem_efficient_sdp(False)
        if shared.cmd_opts.use_zluda_dnn:
            torch.nn.functional.conv2d = conv2d_cudnn_disabled
        devices.device_codeformer = devices.cpu

        if not test(device):
            print(f'ZLUDA device failed to pass basic operation test: index={device.index}, device_name={torch.cuda.get_device_name(device)}')
            torch.cuda.is_available = lambda: False
            devices.backend = 'cpu'
            devices.device = devices.device_esrgan = devices.device_gfpgan = devices.device_interrogate = devices.cpu
