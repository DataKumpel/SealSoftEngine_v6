import wgpu
from rendercanvas import BaseRenderCanvas
from wgpu.gui.auto import WgpuCanvas, run


def setup_drawing_sync(canvas: BaseRenderCanvas):
    # Request adapter and device:
    adapter: wgpu.GPUAdapter = wgpu.gpu.request_adapter_sync(power_preference="high-performance")
    device = adapter.request_device_sync()

    # Configure canvas context:
    context = canvas.get_context("wgpu")



def main():
    print("Hello from sealsoftengine-v6!")

    canvas = WgpuCanvas(size=(800, 600), title="SealSoftEngine V6")

    draw_frame = setup_drawing_sync(canvas)

    canvas.request_draw(draw_frame)

    
    # Start the event loop:
    run()


if __name__ == "__main__":
    main()
