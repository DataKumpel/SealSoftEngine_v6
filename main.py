import wgpu
import logging
from rendercanvas import BaseRenderCanvas
from rendercanvas.contexts import WgpuContext
from wgpu.gui.auto import WgpuCanvas, run

# Basic logging configuration:
logging.basicConfig(
    level=logging.DEBUG,
    style="{", 
    format="{asctime} [{levelname}]: {message}",
)


def setup_drawing_sync(canvas: BaseRenderCanvas):
    # Request adapter and device:
    logging.info("Requesting adapter and device...")
    adapter = wgpu.gpu.request_adapter_sync(power_preference="high-performance")
    device = adapter.request_device_sync()

    # Configure canvas context:
    logging.info("Configuring canvas context...")
    context: WgpuContext = canvas.get_context("wgpu")
    render_texture_format = context.get_preferred_format(adapter)
    context.configure(device=device, format=render_texture_format)

    # Compile shader:
    logging.info("Reading 'shader.wgsl'...")
    with open("shader.wgsl") as shader_file:
        shader_code = shader_file.read()
    logging.info("Compiling shader...")
    shader = device.create_shader_module(label="TRIANGLE_SHADER", code=shader_code)

    # Pipeline layout (TODO)
    logging.info("Creating pipeline layout...")
    pipeline_layout = device.create_pipeline_layout(bind_group_layouts=[])

    # Create render-pipeline:
    logging.info("Create render pipeline...")
    vertex_config = {
        "module": shader,
        "entry_point": "vs_main",
    }
    primitive_config = {
        "topology": wgpu.PrimitiveTopology.triangle_list,
        "front_face": wgpu.FrontFace.ccw,
        "cull_mode": wgpu.CullMode.none,
    }
    fragment_config = {
        "module": shader,
        "entry_point": "fs_main",
        "targets": [
            {
                "format": render_texture_format,
                "blend": {
                    "color": {},
                    "alpha": {},
                },
            },
        ],
    }
    render_pipeline = device.create_render_pipeline(
        label="RENDER_PIPELINE",
        layout=pipeline_layout,
        vertex=vertex_config,
        primitive=primitive_config,
        depth_stencil=None,
        multisample=None,
        fragment=fragment_config,
    )

    # Build the drawing function:
    def draw_frame():
        current_texture: wgpu.GPUTexture = context.get_current_texture()
        command_encoder = device.create_command_encoder()

        # Starting render pass:
        background_color_attachment = {
            "view": current_texture.create_view(),
            "resolve_target": None,
            "clear_value": (0.1, 0.1, 0.1, 1.0), # DARK_GREY
            "load_op": wgpu.LoadOp.clear,
            "store_op": wgpu.StoreOp.store,
        }
        render_pass = command_encoder.begin_render_pass(
            color_attachments=[background_color_attachment],
        )

        render_pass.set_pipeline(render_pipeline)
        render_pass.draw(3)  # 3 vertices, 1 instance
        render_pass.end()

        # Submit commands to queue
        device.queue.submit([command_encoder.finish()])
    
    return draw_frame


def main():
    print("Hello from sealsoftengine-v6!")

    canvas = WgpuCanvas(size=(800, 600), title="SealSoftEngine V6")

    draw_frame = setup_drawing_sync(canvas)

    canvas.request_draw(draw_frame)

    
    # Start the event loop:
    run()


if __name__ == "__main__":
    main()
