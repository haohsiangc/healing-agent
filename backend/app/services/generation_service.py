import os
import io
import base64
import logging
from typing import List
from PIL import Image

logger = logging.getLogger(__name__)


def _make_mock_image(width: int = 512, height: int = 720, seed: int = 0) -> Image.Image:
    """Generate a beautiful gradient placeholder image."""
    import random
    rng = random.Random(seed)
    
    img = Image.new("RGB", (width, height))
    pixels = img.load()
    
    # Pick two random hues for a gradient
    r1, g1, b1 = rng.randint(80, 200), rng.randint(40, 160), rng.randint(120, 255)
    r2, g2, b2 = rng.randint(100, 255), rng.randint(60, 200), rng.randint(80, 200)

    for y in range(height):
        t = y / height
        r = int(r1 + (r2 - r1) * t)
        g = int(g1 + (g2 - g1) * t)
        b = int(b1 + (b2 - b1) * t)
        for x in range(width):
            # Add subtle noise
            noise = rng.randint(-10, 10)
            pixels[x, y] = (
                max(0, min(255, r + noise)),
                max(0, min(255, g + noise)),
                max(0, min(255, b + noise)),
            )
    return img


def _pil_to_base64(img: Image.Image) -> str:
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=85)
    return base64.b64encode(buffer.getvalue()).decode("utf-8")


class GenerationService:
    def __init__(self, mock: bool = True, lora_path: str = "", hf_token: str = ""):
        self.mock = mock
        self.lora_path = lora_path
        self.hf_token = hf_token
        self._pipe = None

    def _load_pipeline(self):
        """Lazy-load the SDXL pipeline only when needed (real GPU mode)."""
        if self._pipe is not None:
            return

        logger.info("Loading SDXL pipeline...")
        import torch
        import numpy as np
        from diffusers import StableDiffusionXLPipeline, EulerAncestralDiscreteScheduler

        model_id = "stabilityai/stable-diffusion-xl-base-1.0"
        pipe = StableDiffusionXLPipeline.from_pretrained(
            model_id,
            torch_dtype=torch.float16,
            use_safetensors=True,
            token=self.hf_token or None,
        ).to("cuda")
        pipe.scheduler = EulerAncestralDiscreteScheduler.from_config(pipe.scheduler.config)

        # Load LoRA weights
        if os.path.exists(self.lora_path):
            pipe.load_lora_weights(self.lora_path, adapter_name="milton-glaser")
        pipe.load_lora_weights(
            "e-n-v-y/envyimpressionismxl01",
            weight_name="EnvyImpressionismXL01.safetensors",
            adapter_name="impressionism",
        )
        pipe.set_adapters(["milton-glaser", "impressionism"], adapter_weights=[1.0, 0.5])

        self._pipe = pipe
        logger.info("SDXL pipeline loaded.")

    def generate(self, prompt: str, num_images: int = 4) -> List[str]:
        """Return list of base64-encoded JPEG images."""
        if self.mock:
            logger.info("Mock image generation for prompt: %s", prompt[:80])
            import random
            seeds = [random.randint(0, 1_000_000) for _ in range(num_images)]
            images = [_make_mock_image(seed=s) for s in seeds]
            return [_pil_to_base64(img) for img in images]

        # Real GPU generation
        try:
            import torch
            import numpy as np

            self._load_pipeline()
            seeds = np.random.randint(0, 1_000_000, num_images)
            generators = [torch.Generator().manual_seed(int(s)) for s in seeds]
            neg_prompt = "man, dark, realistic, words, text, extra, nude, duplicate, ugly"

            results = []
            for i in range(num_images):
                img = self._pipe(
                    "style of Milton Glaser, modern digital impressionism, abstract, " + prompt,
                    negative_prompt=neg_prompt,
                    height=720,
                    width=512,
                    generator=generators[i],
                    num_inference_steps=40,
                    guidance_scale=10,
                ).images[0]
                results.append(_pil_to_base64(img))
            return results

        except Exception as exc:
            logger.error("SDXL generation failed: %s – falling back to mock", exc)
            import random
            return [_pil_to_base64(_make_mock_image(seed=random.randint(0, 999_999))) for _ in range(num_images)]
