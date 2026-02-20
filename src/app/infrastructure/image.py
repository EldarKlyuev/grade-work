"""Image processing service - Pillow-based image resizing"""

from io import BytesIO
from pathlib import Path

from PIL import Image


class PillowImageService:
    """Image processing service using Pillow"""
    
    @staticmethod
    def resize_image(
        image_data: bytes,
        width: int,
        height: int,
        maintain_aspect_ratio: bool = True,
    ) -> bytes:
        """
        Resize image to specified dimensions
        
        Args:
            image_data: Raw image bytes
            width: Target width
            height: Target height
            maintain_aspect_ratio: If True, maintains aspect ratio and fits within bounds
            
        Returns:
            Resized image as bytes
        """
        image = Image.open(BytesIO(image_data))
        
        if maintain_aspect_ratio:
            image.thumbnail((width, height), Image.Resampling.LANCZOS)
        else:
            image = image.resize((width, height), Image.Resampling.LANCZOS)
        
        output = BytesIO()
        
        image_format = image.format if image.format else 'PNG'
        image.save(output, format=image_format)
        
        output.seek(0)
        return output.read()
    
    @staticmethod
    def resize_image_file(
        input_path: Path,
        output_path: Path,
        width: int,
        height: int,
        maintain_aspect_ratio: bool = True,
    ) -> None:
        """
        Resize image file
        
        Args:
            input_path: Path to input image
            output_path: Path to save resized image
            width: Target width
            height: Target height
            maintain_aspect_ratio: If True, maintains aspect ratio
        """
        with open(input_path, 'rb') as f:
            image_data = f.read()
        
        resized_data = PillowImageService.resize_image(
            image_data,
            width,
            height,
            maintain_aspect_ratio,
        )
        
        with open(output_path, 'wb') as f:
            f.write(resized_data)
    
    @staticmethod
    def get_image_info(image_data: bytes) -> dict[str, int | str]:
        """Get image information"""
        image = Image.open(BytesIO(image_data))
        return {
            "width": image.width,
            "height": image.height,
            "format": image.format or "UNKNOWN",
            "mode": image.mode,
        }
