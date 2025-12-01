from rendercanvas.auto import RenderCanvas, loop
from graphics.context import GraphicsContext
from graphics.renderer import Renderer
from scene.camera import Camera
import glm

class GameEngine:
    def __init__(self) -> None:
        self.canvas = RenderCanvas(title="🦭 SealSoftEngine v6", size=(800, 600), vsync=False)
        self.ctx = GraphicsContext(self.canvas)
        self.renderer = Renderer(self.ctx)

        # Game state:
        self.camera = Camera(renderer=self.renderer, 
                             position=glm.vec3(0, 0, 5), 
                             aspect=self.ctx.aspect_ratio)

        self.canvas.request_draw(self.gameloop)
    
    def handle_input(self) -> None:
        ...
    
    def gameloop(self):
        self.handle_input()

        # Game-logic updates here...

        self.renderer.render(scene=...)

        self.canvas.request_draw()

    def run(self):
        loop.run()
    
