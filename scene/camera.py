import glm

class Camera:
    def __init__(self, position: glm.vec3, aspect: float) -> None:
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
        return glm.lookAt(self.position, self.front, self.up)
    
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
