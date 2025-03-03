import base64
import io
import json
from typing import Any, Dict, List

import boto3
from botocore.client import BaseClient
from botocore.config import Config
from PIL import Image, ImageDraw, ImageFont


class BedrockImageModel:
    def __init__(self, model_name: str) -> None:
        self.model_name = model_name

        # Initialize Bedrock client
        self.client = self._init_bedrock_client(
            region="us-east-1",
        )

    def _init_bedrock_client(self, region: str) -> BaseClient:
        retry_config = Config(
            region_name=region,
            retries={
                "max_attempts": 3,
                "mode": "standard",
            },
        )
        return boto3.client(
            service_name="bedrock-runtime", config=retry_config, region_name=region
        )

    def __call__(
        self,
        prompt: str,
        n: int = 1,  # Range: 1 to 5
        quality: str = "premium",
        height: int = 512,
        width: int = 512,
        cfg_scale: float = 6.5,
    ) -> Dict:
        # novaは1024文字まで対応。
        prompt = prompt[:1024]

        body = json.dumps(
            {
                "taskType": "TEXT_IMAGE",
                "textToImageParams": {
                    "text": prompt,
                    # "negativeText": "",
                },
                "imageGenerationConfig": {
                    "numberOfImages": n,
                    "quality": quality,
                    "height": height,
                    "width": width,
                    "cfgScale": cfg_scale,
                    # "seed": 42,
                },
            }
        )
        accept = "application/json"
        content_type = "application/json"

        try:
            response = self.client.invoke_model(
                body=body,
                modelId="amazon.nova-canvas-v1:0",
                accept=accept,
                contentType=content_type,
            )
            return response
        except Exception as e:
            # may occur when length of text promt is more than 512 characters.
            return {"error": str(e)}

    def extract_content(self, response: Dict) -> List[Image.Image]:
        if "error" in response:
            return [self._create_error_image(response["error"])]

        response_body = self._get_body(response)
        # bedrock respond may contain error
        # https://docs.aws.amazon.com/bedrock/latest/userguide/model-parameters-titan-image.html
        if error := response_body.get("error"):
            return [self._create_error_image(error)]

        images = [
            Image.open(io.BytesIO(base64.b64decode(base64_image)))
            for base64_image in response_body.get("images")
        ]
        return images

    def _get_body(self, response: Dict) -> Dict:
        body = response.get("body")
        if body is None:
            raise ValueError("Response body is None")
        return json.loads(body.read())

    def _create_error_image(self, error_message: str) -> Image.Image:
        """エラーメッセージを表示する画像を生成"""
        img = Image.new("RGB", (512, 512), (180, 180, 180))
        font = ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf", 13
        )
        draw = ImageDraw.Draw(img)
        draw.text((10, 200), error_message, fill="black", font=font)
        return img
