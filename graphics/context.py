import wgpu
from rendercanvas import BaseRenderCanvas
from rendercanvas.contexts import WgpuContext


class GraphicsContext:
    def __init__(self, canvas: BaseRenderCanvas) -> None:
        self.canvas = canvas
        self.adapter = wgpu.gpu.request_adapter_sync(power_preference="high-performance")
        self.device = self.adapter.request_device_sync()
        self.present_context: WgpuContext = self.canvas.get_context("wgpu")
        self.render_format = self.present_context.get_preferred_format(self.adapter)

        self.present_context.configure(device=self.device, format=self.render_format)

    @property
    def aspect_ratio(self):
        w, h = self.canvas.get_physical_size()
        return w / h
