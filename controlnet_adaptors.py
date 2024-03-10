from diffusers import ControlNetModel
import torch
import PIL
from controlnet_aux import HEDdetector
import numpy as np
import cv2

def canny_image(input: PIL.Image) -> PIL.Image:    
    image = np.array(input)
    low_threshold = 50
    high_threshold = 100
    image = cv2.Canny(image, low_threshold, high_threshold)
    image = image[:, :, None]
    image = np.concatenate([image, image, image], axis=2)
    return PIL.Image.fromarray(image)

class ControlNetAdaptor:
    def get_pipe() -> ControlNetModel:
        raise NotImplementedError()

    def preprocess(image: PIL.Image) -> PIL.Image:
        raise NotImplementedError()

class CannyControlNet(ControlNetAdaptor):
    pipe = None

    def get_pipe(self) -> ControlNetModel:
        if self.pipe == None:
            self.pipe = get_controlnet_pipe("Canny")
        return self.pipe
    
    def preprocess(self, image: PIL.Image) -> PIL.Image:
        return canny_image(image)
    
class HEDControlNet(ControlNetAdaptor):
    def __init__(self):
        self.hed = HEDdetector.from_pretrained('lllyasviel/ControlNet')

CONTROLNET_MODEL_IDS = {
    "Canny": "thibaud/controlnet-sd21-canny-diffusers",
    "HED": "thibaud/controlnet-sd21-hed-diffusers"
}
def get_controlnet_pipe(name: str):
    return ControlNetModel.from_pretrained(CONTROLNET_MODEL_IDS[name], 
                                           torch_dtype=torch.float16)