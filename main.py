from pyboy import PyBoy
from pyboy import WindowEvent
import pygame
import PIL
import argparse
from frame_processor import DiffusionFrameProcessor

parser = argparse.ArgumentParser()
parser.add_argument('--rom_path', type=str, help='The path to the ROM file', required=True)
args = parser.parse_args()

pygame.init()
screen = pygame.display.set_mode((512, 512))
clock = pygame.time.Clock()
running = True

def image_to_surface(image: PIL.Image) -> pygame.Surface:
    return pygame.image.fromstring(image.tobytes(), image.size, image.mode)

def handle_gameboy_input_forwarding(event: pygame.event.Event, pyboy: PyBoy):
    if event.key == pygame.K_RETURN:
        pyboy.send_input(WindowEvent.PRESS_BUTTON_START if event.type == pygame.KEYDOWN else WindowEvent.RELEASE_BUTTON_START)
    if event.key == pygame.K_LEFT:
        pyboy.send_input(WindowEvent.PRESS_ARROW_LEFT if event.type == pygame.KEYDOWN else WindowEvent.RELEASE_ARROW_LEFT)
    if event.key == pygame.K_RIGHT:
        pyboy.send_input(WindowEvent.PRESS_ARROW_RIGHT if event.type == pygame.KEYDOWN else WindowEvent.RELEASE_ARROW_RIGHT)
    if event.key == pygame.K_UP:
        pyboy.send_input(WindowEvent.PRESS_ARROW_UP if event.type == pygame.KEYDOWN else WindowEvent.RELEASE_ARROW_UP)
    if event.key == pygame.K_DOWN:
        pyboy.send_input(WindowEvent.PRESS_ARROW_DOWN if event.type == pygame.KEYDOWN else WindowEvent.RELEASE_ARROW_DOWN)
    if event.key == pygame.K_z:
        pyboy.send_input(WindowEvent.PRESS_BUTTON_A if event.type == pygame.KEYDOWN else WindowEvent.RELEASE_BUTTON_A)
    if event.key == pygame.K_x:
        pyboy.send_input(WindowEvent.PRESS_BUTTON_B if event.type == pygame.KEYDOWN else WindowEvent.RELEASE_BUTTON_B)
    if event.key == pygame.K_SPACE:
        pyboy.send_input(WindowEvent.PRESS_SPEED_UP if event.type == pygame.KEYDOWN else WindowEvent.RELEASE_SPEED_UP)

render_every_n_frame = 30
frame_idx = 0
enable_diffusion = False
last_frame = None
frame_processor = DiffusionFrameProcessor()
with PyBoy(args.rom_path, window_type="headless") as pyboy:
    while running:
        skip_frame = (frame_idx % render_every_n_frame) != 0
        frame_idx += 1
        pyboy_quit = pyboy.tick()
        if pyboy_quit:
            raise Exception("PyBoy quit")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise Exception("PyGame quit")
            if event.type in (pygame.KEYDOWN, pygame.KEYUP):
                if event.key == pygame.K_p and event.type == pygame.KEYUP:
                    enable_diffusion = not enable_diffusion
                handle_gameboy_input_forwarding(event, pyboy)

        if not skip_frame:
            this_frame = pyboy.screen_image().resize((512, 512))
            if not enable_diffusion:
                this_frame_processed = this_frame
            else:
                this_frame_processed = frame_processor.process(last_frame, this_frame)
            last_frame = this_frame_processed
            this_frame_processed_surface = image_to_surface(this_frame_processed)
            screen.blit(this_frame_processed_surface, (0, 0))
            pygame.display.flip()
        clock.tick(60)
    pygame.quit()

