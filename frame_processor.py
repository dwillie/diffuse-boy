import PIL
from diffusers import StableDiffusionControlNetImg2ImgPipeline
import torch

from controlnet_adaptors import CannyControlNet, ControlNetAdaptor 

class FrameProcessor:
    def process(self, input: PIL.Image) -> PIL.Image:
        raise NotImplementedError()
    
class DiffusionFrameProcessor(FrameProcessor):
    controlnet_adaptor: ControlNetAdaptor
    stable_diffusion_pipe: StableDiffusionControlNetImg2ImgPipeline

    def __init__(self):
        self.prompt = "A full-colour high-resolution screenshot of a beautiful colourful vibrant pokemon game, best quality, extremely detailed"
        self.negative_prompt = "monochrome, greyscale, lowres, bad anatomy, worst quality, low quality"
        self.controlnet_adaptor = CannyControlNet()
        self.stable_diffusion_pipe = StableDiffusionControlNetImg2ImgPipeline.from_pretrained(
            "stabilityai/sd-turbo", 
            safety_checker=None, 
            torch_dtype=torch.float16, 
            controlnet=self.controlnet_adaptor.get_pipe(),
        )
        self.stable_diffusion_pipe.to("cuda")
        self.generator = torch.manual_seed(0)

    def process(self, last_frame: PIL.Image, this_frame: PIL.Image) -> PIL.Image:
        return self.stable_diffusion_pipe(
            self.prompt, 
            negative_prompt=self.negative_prompt, 
            guess_mode=True,
            generator=self.generator, 
            image=last_frame if last_frame else this_frame,
            control_image=self.controlnet_adaptor.preprocess(this_frame),
            num_inference_steps=6, 
            strength=0.999, 
            guidance_scale=1.5,
            controlnet_conditioning_scale=2.0,
            control_guidance_start=0,
            control_guidance_end=1,
        ).images[0]