import os
import pytest
import time


class TestDrawThings:
    """Test DrawThings image generation integration."""

    def test_drawthings_connectivity(self, check_drawthings):
        """Test that we can connect to DrawThings."""
        assert check_drawthings is True

    def test_generate_image(self, check_drawthings, output_dir):
        """Test image generation with DrawThings."""
        from storyteller.modules.st.image_gen.draw_things_text_to_image import (
            generate_draw_things_text_to_image,
        )

        prompt = "A cute cat sitting on a rug, colorful illustration"

        result, returned_prompt, success = generate_draw_things_text_to_image(
            prompt=prompt,
            output_dir=str(output_dir),
            num_inference_steps=10,
            guidance_scale=7.0,
            width=512,
            height=512,
        )

        assert success is True
        assert result is not None
        assert "Error" not in result
        assert "http://" in result or ".png" in result or ".jpg" in result

    def test_generate_simple_image(self, check_drawthings, output_dir):
        """Test simple image generation."""
        from storyteller.modules.st.image_gen.draw_things_text_to_image import (
            generate_draw_things_text_to_image,
        )

        prompt = "A simple blue circle"

        result, returned_prompt, success = generate_draw_things_text_to_image(
            prompt=prompt,
            output_dir=str(output_dir),
            num_inference_steps=5,
            guidance_scale=7.0,
            width=256,
            height=256,
        )

        assert success is True
        assert result is not None