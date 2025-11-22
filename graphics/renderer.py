import wgpu
from pathlib import Path
from .context import GraphicsContext


class Renderer:
    def __init__(self, ctx: GraphicsContext):
        self.ctx = ctx
        self.depth_stencil = self._create_depth_stencil()

        # Bind Group Layouts:
        self.global_bgl = self._create_global_layout()

        # Compile shader:
        self.shader = self._compile_shader("shader.wgsl")

        # Pipeline configurations:
        self.vb_layout = self._create_vb_layout()
        self.vertex_config = self._create_vertex_config()
        self.primitive_config = self._create_primitive_config()
        self.fragment_config = self._create_fragment_config()

        self.pipeline = self._create_pipeline()

    def _compile_shader(self, shader_path: str) -> wgpu.GPUShaderModule:
        code = Path(shader_path).read_text()
        return self.ctx.device.create_shader_module(label="SHADER", code=code)

    def _create_vertex_config(self) -> wgpu.VertexState:
        return wgpu.VertexState(
            module=self.shader,
            entry_point="vs_main",
            buffers=[self.vb_layout],
        )

    def _create_vb_layout(self) -> wgpu.VertexBufferLayout:
        position_attrib = wgpu.VertexAttribute(
            format=wgpu.VertexFormat.float32x3,
            offset=0,
            shader_location=0,
        )
        color_attrib = wgpu.VertexAttribute(
            format=wgpu.VertexFormat.float32x3,
            offset=12,  # 3 floats (4 bytes) offset
            shader_location=1,
        )
        
        return wgpu.VertexBufferLayout(
            array_stride=24,  # 6 floats * 4 bytes
            step_mode=wgpu.VertexStepMode.vertex,
            attributes=[position_attrib, color_attrib],
        )
    
    def _create_primitive_config(self):
        # The default config is just fine :)
        return wgpu.PrimitiveState()
    
    def _create_fragment_config(self):
        color_target = wgpu.ColorTargetState(
            format=self.ctx.render_format,
            blend=wgpu.BlendState(color={}, alpha={}),
        )
        return wgpu.FragmentState(
            module=self.shader,
            entry_point="fs_main",
            targets=[color_target],
        )

    def _create_depth_stencil(self) -> wgpu.DepthStencilState:
        return wgpu.DepthStencilState(
            format=wgpu.TextureFormat.depth24plus,
            depth_write_enabled=True,
            depth_compare=wgpu.CompareFunction.less,
        )
    
    def _create_global_layout(self) -> wgpu.GPUBindGroupLayout:
        return self.ctx.device.create_bind_group_layout(
            label="GLOBAL_BIND_GROUP_LAYOUT",
            entries=[
                wgpu.BindGroupLayoutEntry(
                    binding=0,
                    visibility=wgpu.ShaderStage.VERTEX,
                    buffer=wgpu.BufferBindingLayout(),
                ),
            ],
        )
    
    def _create_pipeline(self) -> wgpu.GPURenderPipeline:
        pipeline_layout = self.ctx.device.create_pipeline_layout(
            label="PIPELINE_LAYOUT",
            bind_group_layouts=[self.global_bgl],
        )
        
        return self.ctx.device.create_render_pipeline(
            label="RENDER_PIPELINE",
            layout=pipeline_layout,
            vertex=self.vertex_config,
            primitive=self.primitive_config,
            depth_stencil=self.depth_stencil,
            multisample=None,
            fragment=self.fragment_config,
        )