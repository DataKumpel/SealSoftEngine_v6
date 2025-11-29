import glm
import wgpu
import numpy as np
from graphics.renderer import Renderer

class Camera:
    def __init__(self, renderer: Renderer, position: glm.vec3, aspect: float) -> None:
        self.renderer = renderer
        self.device = renderer.ctx.device
        self.uniform_buffer = self._create_uniform_buffer()
        self.bind_group = self._create_bind_group()

        self.position = position
        self.front = glm.vec3(0, 0, -1)
        self.up = glm.vec3(0, 1, 0)
        self.yaw = -90.0
        self.pitch = 0.0
        self.fovy = 60.0
        self.clip_near = 0.1
        self.clip_far = 100.0
        self.aspect = aspect

    def get_view_matrix(self) -> glm.mat4x4:
        return glm.lookAt(self.position, self.position + self.front, self.up)
    
    def get_projection_matrix(self) -> glm.mat4x4:
        return glm.perspective(glm.radians(self.fovy), self.aspect, self.clip_near, self.clip_far)
    
    def update_direction(self, dx, dy, sensitivity=0.1) -> None:
        self.yaw += dx * sensitivity
        self.pitch -= dy * sensitivity
        self.pitch = max(-89.0, min(89.0, self.pitch))

        # Calc new front vector:
        front = glm.vec3()
        front.x = glm.cos(glm.radians(self.yaw)) * glm.cos(glm.radians(self.pitch))
        front.y = glm.sin(glm.radians(self.pitch))
        front.z = glm.sin(glm.radians(self.yaw)) * glm.cos(glm.radians(self.pitch))
        self.front = glm.normalize(front)

    def update(self):
        view = self.get_view_matrix()
        proj = self.get_projection_matrix()

        view_proj_data: np.ndarray = np.array([view, proj], dtype=np.float32)
        
        self.device.queue.write_buffer(self.uniform_buffer, 0, view_proj_data.tobytes())

    def _create_uniform_buffer(self) -> wgpu.GPUBuffer:
        return self.device.create_buffer(
            label="CAMERA_UNIFORM_BUFFER",
            size=(4 * 4 * 4) * 2,  # 2x 4x4 matrices (view + proj)
            usage=wgpu.BufferUsage.UNIFORM | wgpu.BufferUsage.COPY_DST,
        )
    
    def _create_bind_group(self) -> wgpu.GPUBindGroup:
        return self.device.create_bind_group(
            label="CAMERA_BIND_GROUP",
            layout=self.renderer.global_bgl,
            entries=[
                wgpu.BindGroupEntry(
                    binding=0,
                    resource=wgpu.BufferBinding(buffer=self.uniform_buffer),
                ),
            ],
        )
