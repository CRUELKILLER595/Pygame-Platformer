
import asyncio
import pygame

pygame.init()

WIDTH = 960
HEIGHT = 640

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("PixelBound - Web Runtime Test")

title_font = pygame.font.Font(None, 64)
body_font = pygame.font.Font(None, 32)

running = True


async def main():

    global running

    while running:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        screen.fill((25, 30, 45))

        title = title_font.render(
            "PixelBound - Web Runtime Test",
            True,
            (230, 240, 255)
        )

        subtitle = body_font.render(
            "Browser Runtime Test",
            True,
            (120, 190, 230)
        )

        instruction = body_font.render(
            "Press ESC to exit",
            True,
            (190, 195, 205)
        )

        screen.blit(
            title,
            title.get_rect(center=(WIDTH // 2, 240))
        )

        screen.blit(
            subtitle,
            subtitle.get_rect(center=(WIDTH // 2, 320))
        )

        screen.blit(
            instruction,
            instruction.get_rect(center=(WIDTH // 2, 420))
        )

        pygame.display.flip()

        # Required cooperative yield for Pygbag.
        await asyncio.sleep(0)


asyncio.run(main())
