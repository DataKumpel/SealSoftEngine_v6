import wgpu
import numpy as np


def create_cube_data() -> tuple[np.ndarray, np.ndarray]:
    vertices = np.array([
        # Front face (RED)
        [-0.5, -0.5, 0.5, 1.0, 0.0, 0.0], # 0
        [ 0.5, -0.5, 0.5, 1.0, 0.0, 0.0], # 1
        [ 0.5,  0.5, 0.5, 1.0, 0.0, 0.0], # 2
        [-0.5,  0.5, 0.5, 1.0, 0.0, 0.0], # 3

        # Back face (GREEN)
        [ 0.5, -0.5, -0.5, 0.0, 1.0, 0.0], # 4
        [-0.5, -0.5, -0.5, 0.0, 1.0, 0.0], # 5
        [-0.5,  0.5, -0.5, 0.0, 1.0, 0.0], # 6
        [ 0.5,  0.5, -0.5, 0.0, 1.0, 0.0], # 7

        # Top face (BLUE)
        [-0.5,  0.5,  0.5, 0.0, 0.0, 1.0], # 8
        [ 0.5,  0.5,  0.5, 0.0, 0.0, 1.0], # 9
        [ 0.5,  0.5, -0.5, 0.0, 0.0, 1.0], # 10
        [-0.5,  0.5, -0.5, 0.0, 0.0, 1.0], # 11

        # Bottom face (YELLOW)
        [-0.5, -0.5, -0.5, 1.0, 1.0, 0.0], # 12
        [ 0.5, -0.5, -0.5, 1.0, 1.0, 0.0], # 13
        [ 0.5, -0.5,  0.5, 1.0, 1.0, 0.0], # 14
        [-0.5, -0.5,  0.5, 1.0, 1.0, 0.0], # 15

        # Right face (MAGENTA)
        [ 0.5, -0.5,  0.5, 1.0, 0.0, 1.0], # 16
        [ 0.5, -0.5, -0.5, 1.0, 0.0, 1.0], # 17
        [ 0.5,  0.5, -0.5, 1.0, 0.0, 1.0], # 18
        [ 0.5,  0.5,  0.5, 1.0, 0.0, 1.0], # 19

        # Left face (CYAN)
        [-0.5, -0.5, -0.5, 0.0, 1.0, 1.0], # 20
        [-0.5, -0.5,  0.5, 0.0, 1.0, 1.0], # 21
        [-0.5,  0.5,  0.5, 0.0, 1.0, 1.0], # 22
        [-0.5,  0.5, -0.5, 0.0, 1.0, 1.0], # 23
    ], dtype=np.float32)

    indices = np.array([
         0,  1,  2,  2,  3,  0,  # Front
         4,  5,  6,  6,  7,  4,  # Back
         8,  9, 10, 10, 11,  8,  # Top
        12, 13, 14, 14, 15, 12,  # Bottom
        16, 17, 18, 18, 19, 16,  # Right
        20, 21, 22, 22, 23, 20,  # Left
    ], dtype=np.uint32)

    return vertices, indices


class Mesh:
    def __init__(self, device: wgpu.GPUDevice, vertices: np.ndarray, indices=None) -> None:
        self.device = device
        self.vertex_count = len(vertices)
        self.vertex_buffer = device.create_buffer_with_data(data=vertices, 
                                                            usage=wgpu.BufferUsage.VERTEX)

        if indices is not None:
            self.index_count = len(indices)
            self.index_buffer = device.create_buffer_with_data(data=indices, 
                                                               usage=wgpu.BufferUsage.INDEX)
        else:
            self.index_count = 0
            self.index_buffer = None


def create_cube_mesh(device: wgpu.GPUDevice) -> Mesh:
    vertices, indices = create_cube_data()
    return Mesh(device, vertices, indices)

