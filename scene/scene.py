from .camera import Camera

class Scene:
    def __init__(self, camera: Camera) -> None:
        self.camera = camera
        self.entities = []

    def add(self, entity) -> None:
        self.entities.append(entity)

    def update(self, dt: float) -> None:
        self.camera.update()
        for entity in self.entities:
            entity.update()
    
