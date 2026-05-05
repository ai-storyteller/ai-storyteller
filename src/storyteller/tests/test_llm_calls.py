import pytest


class TestOllamaLLM:
    """Test Ollama LLM integration."""

    def test_ollama_connectivity(self, check_ollama):
        """Test that we can connect to Ollama."""
        assert check_ollama is True

    def test_generate_story(self, check_ollama, output_dir):
        """Test story generation with Ollama."""
        from storyteller.modules.st.llm_calls import (
            Character,
            generate_story,
        )
        from storyteller.modules.common.progress_bar import ProgressBar

        characters = [
            Character(
                name="Luna",
                interests=["Adventures", "Reading"],
                favourite_animal="Cat",
                age=9,
                eye_color="green",
                hair_color="brown",
                skin_color="light",
                height=130,
                identity="girl",
            )
        ]

        class DummyProgressBar:
            def update(self, **kwargs):
                pass

        progress = DummyProgressBar()

        result = generate_story(
            base_prompt="Write a very short story (50 words) about a brave cat.",
            characters=characters,
            progress_bar=progress,
        )

        assert result is not None
        assert result.story is not None
        assert len(result.story) > 0
        assert result.title is not None

    def test_generate_story_simple(self, check_ollama):
        """Test simple story generation with minimal prompt."""
        from storyteller.modules.st.llm_calls import (
            Character,
            generate_story,
        )
        from storyteller.modules.common.progress_bar import ProgressBar

        characters = [
            Character(
                name="Max",
                interests=["Sports"],
                favourite_animal="Dog",
                age=8,
            )
        ]

        class DummyProgressBar:
            def update(self, **kwargs):
                pass

        progress = DummyProgressBar()

        result = generate_story(
            base_prompt="Write a 30-word story about friendship.",
            characters=characters,
            progress_bar=progress,
            reading_level="early",
        )

        assert result.story is not None
        assert len(result.story) > 0
        assert result.title is not None
        assert len(result.key_sd_prompts) > 0
