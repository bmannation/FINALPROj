import asyncio
import pygame
from engine import SceneManager
from data.dialogue import INTRO_TEXT  # noqa: F401 — imported for side-effect-free availability


async def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Choose Ur Own Adventure")
    clock = pygame.time.Clock()

    manager = SceneManager(screen)
    manager.register_all()
    manager.switch_to("title", None)

    while True:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            manager.handle_event(event)
        manager.update(dt)
        manager.draw(screen)
        pygame.display.flip()
        await asyncio.sleep(0)


asyncio.run(main())
