import wgpu
import logging
import numpy as np
try:
    from pyglm import glm
except ImportError:
    import glm
import time
from pathlib import Path
from rendercanvas import BaseRenderCanvas
from rendercanvas.contexts import WgpuContext
from wgpu.gui.auto import WgpuCanvas, run

# Basic logging configuration:
logging.basicConfig(
    level=logging.DEBUG,
    style="{", 
    format="{asctime} [{levelname}]: {message}",
)

def load_shader(path: str) -> str:
    return Path(path).read_text()

def create_cube_data() -> tuple[np.ndarray, np.ndarray]:
    vertices = np.array([
        # Front face (RED)
        [-0.5, -0.5, 0.5, 1.0, 0.0, 0.0],
        [ 0.5, -0.5, 0.5, 1.0, 0.0, 0.0],
        [ 0.5,  0.5, 0.5, 1.0, 0.0, 0.0],
        [-0.5,  0.5, 0.5, 1.0, 0.0, 0.0],

        # Back face (GREEN)
        [-0.5, -0.5, -0.5, 0.0, 1.0, 0.0],
        [ 0.5, -0.5, -0.5, 0.0, 1.0, 0.0],
        [ 0.5,  0.5, -0.5, 0.0, 1.0, 0.0],
        [-0.5,  0.5, -0.5, 0.0, 1.0, 0.0],

        # Top face (BLUE)
        [-0.5,  0.5, -0.5, 0.0, 0.0, 1.0],
        [-0.5,  0.5,  0.5, 0.0, 0.0, 1.0],
        [ 0.5,  0.5,  0.5, 0.0, 0.0, 1.0],
        [ 0.5,  0.5, -0.5, 0.0, 0.0, 1.0],

        # Bottom face (YELLOW)
        [-0.5, -0.5, -0.5, 1.0, 1.0, 0.0],
        [-0.5, -0.5,  0.5, 1.0, 1.0, 0.0],
        [ 0.5, -0.5,  0.5, 1.0, 1.0, 0.0],
        [ 0.5, -0.5, -0.5, 1.0, 1.0, 0.0],

        # Right face (MAGENTA)
        [ 0.5, -0.5, -0.5, 1.0, 0.0, 1.0],
        [ 0.5,  0.5, -0.5, 1.0, 0.0, 1.0],
        [ 0.5,  0.5,  0.5, 1.0, 0.0, 1.0],
        [ 0.5, -0.5,  0.5, 1.0, 0.0, 1.0],

        # Left face (CYAN)
        [-0.5, -0.5, -0.5, 0.0, 1.0, 1.0],
        [-0.5,  0.5, -0.5, 0.0, 1.0, 1.0],
        [-0.5,  0.5,  0.5, 0.0, 1.0, 1.0],
        [-0.5, -0.5,  0.5, 0.0, 1.0, 1.0],
    ], dtype=np.float32)

    indices = np.array([
         0,  1,  2,  2,  3,  0,  # Front
         4,  6,  5,  6,  4,  7,  # Back
         8,  9, 10, 10, 11,  8,  # Top
        12, 14, 13, 14, 12, 15,  # Bottom
        16, 17, 18, 18, 19, 16,  # Right
        20, 22, 21, 22, 20, 23,  # Left
    ], dtype=np.uint32)

    return vertices, indices

def setup_drawing_sync(canvas: BaseRenderCanvas):
    logging.info("Requesting adapter and device...")
    adapter = wgpu.gpu.request_adapter_sync(power_preference="high-performance")
    device = adapter.request_device_sync()

    logging.info("Configuring canvas context...")
    context: WgpuContext = canvas.get_context("wgpu")
    render_texture_format = context.get_preferred_format(adapter)
    context.configure(device=device, format=render_texture_format)

    logging.info("Reading 'shader.wgsl'...")
    shader_code = load_shader("shader.wgsl")

    logging.info("Compiling shader...")
    shader = device.create_shader_module(label="TRIANGLE_SHADER", code=shader_code)

    logging.info("Loading cube data...")
    vertices, indices = create_cube_data()

    logging.info("Creating vertex buffer...")
    vertex_buffer = device.create_buffer_with_data(
        label="VERTEX_BUFFER",
        data=vertices,
        usage=wgpu.BufferUsage.VERTEX,
    )

    logging.info("Creating index buffer...")
    index_buffer = device.create_buffer_with_data(
        label="INDEX_BUFFER",
        data=indices,
        usage=wgpu.BufferUsage.INDEX,
    )

    logging.info("Create uniform buffer for MVP-matrices...")
    uniform_buffer = device.create_buffer(
        label="MVP_MATRIX",
        size=64,  # mat4x4<f32> == 4 * 4 * (32 / 8) Bytes
        usage=wgpu.BufferUsage.UNIFORM | wgpu.BufferUsage.COPY_DST,
    )

    logging.info("Creating bind group layout...")
    bind_group_layout = device.create_bind_group_layout(
        label="BIND_GROUP_LAYOUT",
        entries=[
            wgpu.BindGroupLayoutEntry(
                binding=0,
                visibility=wgpu.ShaderStage.VERTEX,
                buffer=wgpu.BufferBindingLayout(type=wgpu.BufferBindingType.uniform),
            ),
        ],
    )

    logging.info("Creating bind group...")
    bind_group = device.create_bind_group(
        label="UNIFORM_BIND_GROUP",
        layout=bind_group_layout,
        entries=[
            wgpu.BindGroupEntry(
                binding=0,
                resource=wgpu.BufferBinding(
                    buffer=uniform_buffer,
                    offset=0,
                    size=64,
                ),
            ),
        ],
    )

    logging.info("Creating pipeline layout...")
    pipeline_layout = device.create_pipeline_layout(
        label="PIPELINE_LAYOUT",
        bind_group_layouts=[bind_group_layout],
    )

    logging.info("Create depth stencil...")
    depth_stencil = wgpu.DepthStencilState(
        format=wgpu.TextureFormat.depth24plus,
        depth_write_enabled=True,
        depth_compare=wgpu.CompareFunction.less,
    )

    logging.info("Create depth texture...")
    depth_texture = device.create_texture(
        label="DEPTH_TEXTURE",
        size=tuple(*canvas.get_physical_size(), 1),
        format=wgpu.TextureFormat.depth24plus,
        usage=wgpu.TextureUsage.RENDER_ATTACHMENT,
    )
    depth_view = depth_texture.create_view()

    logging.info("Create render pipeline...")
    vertex_config = wgpu.VertexState(
        module=shader,
        entry_point="vs_main",
        buffers=[
            wgpu.VertexBufferLayout(
                array_stride=6 * 4,  # 6 floats * 4 bytes
                step_mode=wgpu.VertexStepMode.vertex,
                attributes=[
                    wgpu.VertexAttribute(
                        format=wgpu.VertexFormat.float32x3,
                        offset=0,
                        shader_location=0,  # position
                    ),
                    wgpu.VertexAttribute(
                        format=wgpu.VertexFormat.float32x3,
                        offset=3 * 4,  # 3 floats offset
                        shader_location=1,  # color
                    ),
                ],
            ),
        ],
    )
    primitive_config = wgpu.PrimitiveState(
        topology=wgpu.PrimitiveTopology.triangle_list,
        front_face=wgpu.FrontFace.ccw,
        cull_mode=wgpu.CullMode.back,
    )
    fragment_config = wgpu.FragmentState(
        module=shader,
        entry_point="fs_main",
        targets=[
            wgpu.ColorTargetState(
                format=render_texture_format,
                blend=wgpu.BlendState(color={}, alpha={})
            )
        ]
    )
    render_pipeline = device.create_render_pipeline(
        label="RENDER_PIPELINE",
        layout=pipeline_layout,
        vertex=vertex_config,
        primitive=primitive_config,
        depth_stencil=None,
        multisample=None,
        fragment=fragment_config,
    )

    # Start time for animations:
    start_time = time.time()

    # Build the drawing function:
    def draw_frame():
        current_time = time.time() - start_time

        # Model matrix with rotation around y and x axis:
        model = glm.mat4(1.0)
        model = glm.rotate(model, current_time * 0.5, glm.vec3(0, 1, 0))
        model = glm.rotate(model, current_time * 0.3, glm.vec3(1, 0, 0))

        # View matrix:
        view = glm.lookAt(
            glm.vec3(0, 0, 3),
            glm.vec3(0, 0, 0),
            glm.vec3(0, 1, 0),
        )

        # Projection matrix:
        width, height = canvas.get_physical_size()
        aspect_ratio = width / height
        projection = glm.perspective(glm.radians(66.0), aspect_ratio, 0.1, 100.0)

        # Combine mvp:
        mvp = projection * view * model
        mvp_array = np.array(mvp, dtype=np.float32)
        device.queue.write_buffer(uniform_buffer, 0, mvp_array)
        
        # Rendering:
        current_texture: wgpu.GPUTexture = context.get_current_texture()
        command_encoder = device.create_command_encoder(label="COMMAND_ENCODER")

        # Starting render pass:
        render_pass = command_encoder.begin_render_pass(
            color_attachments=[
                wgpu.RenderPassColorAttachment(
                    view=current_texture.create_view(),
                    resolve_target=None,
                    clear_value=(0.1, 0.1, 0.1, 1.0),
                    load_op=wgpu.LoadOp.clear,
                    store_op=wgpu.StoreOp.store,
                ),
            ],
            depth_stencil_attachment=wgpu.RenderPassDepthStencilAttachment(
                view=depth_view,
                depth_clear_value=1.0,
                depth_load_op=wgpu.LoadOp.clear,
                depth_store_op=wgpu.StoreOp.store,
            ),
        )

        render_pass.set_pipeline(render_pipeline)
        render_pass.set_bind_group(0, bind_group, [], 0, 1)
        render_pass.set_vertex_buffer(0, vertex_buffer, 0, vertices.nbytes)
        render_pass.set_index_buffer(index_buffer, wgpu.IndexFormat.uint32, 0, indices.nbytes)
        render_pass.draw_indexed(len(indices))
        render_pass.end()

        # Submit commands to queue
        device.queue.submit([command_encoder.finish()])

        # Request next frame:
        canvas.request_draw(draw_frame)
    
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
