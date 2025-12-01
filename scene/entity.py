#import glm  #deprecated!
from pyglm import glm
import wgpu
import numpy as np
from graphics.renderer import Renderer


class Entity:
    def __init__(self, 
                 renderer: Renderer, 
                 mesh, 
                 position: glm.vec3 | None = None, 
                 rotation: glm.vec3 | None = None, 
                 scale: glm.vec3 | None = None) -> None:
        self.renderer = renderer
        self.mesh = mesh

        # Transform data:
        self.position = position or glm.vec3(0, 0, 0)
        self.rotation = rotation or glm.vec3(0, 0, 0)
        self.scale = scale or glm.vec3(1, 1, 1)

        # GROUP 1 wgpu resources:
        self.uniform_buffer = self._create_uniform_buffer()
        self.bind_group = self._create_bind_group()

        # Calculate initial matrix:
        self.update_matrix()

    def update(self, dt: float):
        """Update logic every frame."""

    def update_matrix(self) -> None:
        matrix = glm.mat4(1.0)
        matrix = glm.translate(matrix, self.position)
        matrix = glm.rotate(matrix, glm.radians(self.rotation.x), glm.vec3(1, 0, 0))
        matrix = glm.rotate(matrix, glm.radians(self.rotation.y), glm.vec3(0, 1, 0))
        matrix = glm.rotate(matrix, glm.radians(self.rotation.z), glm.vec3(0, 0, 1))
        matrix = glm.scale(matrix, self.scale)

        # Transfer data to GPU:
        data = np.array(matrix, dtype=np.float32).tobytes()
        self.renderer.ctx.device.queue.write_buffer(self.uniform_buffer, 0, data)

    def _create_uniform_buffer(self) -> wgpu.GPUBuffer:
        return self.renderer.ctx.device.create_buffer(
            label="ENTITY_MODEL_BUFFER",
            size=64,  # 4x4 float32 (4 bytes) matrix
            usage=wgpu.BufferUsage.UNIFORM | wgpu.BufferUsage.COPY_DST,
        )

    def _create_bind_group(self) -> wgpu.GPUBindGroup:
        return self.renderer.ctx.device.create_bind_group(
            label="ENTITY_BIND_GROUP",
            layout=self.renderer.object_bgl,
            entries=[
                wgpu.BindGroupEntry(
                    binding=0,
                    resource=wgpu.BufferBinding(buffer=self.uniform_buffer)
                ),
            ],
        )
