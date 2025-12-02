"""Unit tests for cyberette.helpers.ResponseParser."""
import pytest
from cyberette_sdk.utils import ResponseParser


# Test data fixtures
IMAGE_RESPONSE = {
    "metadata": None,
    "deepfake": {
        "name": "ResNet50",
        "version": 2,
        "detection": {
            "verdict": "REAL",
            "score": 95,
        },
    },
}

AUDIO_RESPONSE = {
    "sample_rate": 16000,
    "deepfake": {
        "name": "WaveNet",
        "version": 1,
        "detection": {
            "verdict": "DEEPFAKE",
            "percentage": 87,
            "segments": [
                {"start": 0, "end": 5, "score": 92, "verdict": "DEEPFAKE"},
                {"start": 5, "end": 10, "score": 75, "verdict": "SUSPICIOUS"},
            ],
        },
    },
}

VIDEO_RESPONSE = {
    "frame_rate": 30,
    "deepfake": {
        "name": "FaceForensics",
        "version": 3,
        "detection": {
            "verdict": "REAL",
            "percentage": 92,
            "segments": [
                {"start": 0, "end": 10, "score": 94, "verdict": "REAL"},
            ],
        },
    },
}

VIDEO_AUDIO_RESPONSE = {
    "verdict": "DEEPFAKE",
    "percentage": 85,
    "audio": {
        "deepfake": {
            "name": "WaveNet",
            "version": 1,
            "detection": {
                "verdict": "DEEPFAKE",
                "percentage": 88,
            },
        },
    },
    "video": {
        "deepfake": {
            "name": "FaceForensics",
            "version": 3,
            "detection": {
                "verdict": "DEEPFAKE",
                "percentage": 82,
            },
        },
    },
}


class TestSafeGet:
    """Tests for safe_get helper function."""

    def test_safe_get_single_key(self):
        data = {"key": "value"}
        assert ResponseParser.safe_get(data, ["key"]) == "value"

    def test_safe_get_nested_keys(self):
        data = {"level1": {"level2": {"level3": "value"}}}
        assert ResponseParser.safe_get(data, ["level1", "level2", "level3"]) == "value"

    def test_safe_get_missing_key_returns_default(self):
        data = {"key": "value"}
        assert ResponseParser.safe_get(data, ["missing"]) is None
        assert ResponseParser.safe_get(data, ["missing"], default="default") == "default"

    def test_safe_get_missing_nested_key_returns_default(self):
        data = {"level1": {"level2": "value"}}
        assert ResponseParser.safe_get(data, ["level1", "missing", "level3"]) is None

    def test_safe_get_non_dict_input_returns_default(self):
        assert ResponseParser.safe_get("not_a_dict", ["key"]) is None
        assert ResponseParser.safe_get(None, ["key"], default="default") == "default"


class TestGetModelName:
    """Tests for get_model_name."""

    def test_get_model_name_image(self):
        assert ResponseParser.get_model_name(IMAGE_RESPONSE) == "ResNet50"

    def test_get_model_name_audio(self):
        assert ResponseParser.get_model_name(AUDIO_RESPONSE) == "WaveNet"

    def test_get_model_name_video(self):
        assert ResponseParser.get_model_name(VIDEO_RESPONSE) == "FaceForensics"

    def test_get_model_name_multimodal_video(self):
        assert ResponseParser.get_model_name(VIDEO_AUDIO_RESPONSE, media="video") == "FaceForensics"

    def test_get_model_name_multimodal_audio(self):
        assert ResponseParser.get_model_name(VIDEO_AUDIO_RESPONSE, media="audio") == "WaveNet"

    def test_get_model_name_missing(self):
        assert ResponseParser.get_model_name({}) is None


class TestGetModelVersion:
    """Tests for get_model_version."""

    def test_get_model_version_image(self):
        assert ResponseParser.get_model_version(IMAGE_RESPONSE) == 2

    def test_get_model_version_audio(self):
        assert ResponseParser.get_model_version(AUDIO_RESPONSE) == 1

    def test_get_model_version_video(self):
        assert ResponseParser.get_model_version(VIDEO_RESPONSE) == 3

    def test_get_model_version_multimodal_video(self):
        assert ResponseParser.get_model_version(VIDEO_AUDIO_RESPONSE, media="video") == 3

    def test_get_model_version_multimodal_audio(self):
        assert ResponseParser.get_model_version(VIDEO_AUDIO_RESPONSE, media="audio") == 1

    def test_get_model_version_missing(self):
        assert ResponseParser.get_model_version({}) is None


class TestGetDetectionVerdict:
    """Tests for get_detection_verdict."""

    def test_get_detection_verdict_image(self):
        assert ResponseParser.get_detection_verdict(IMAGE_RESPONSE) == "REAL"

    def test_get_detection_verdict_audio(self):
        assert ResponseParser.get_detection_verdict(AUDIO_RESPONSE) == "DEEPFAKE"

    def test_get_detection_verdict_video(self):
        assert ResponseParser.get_detection_verdict(VIDEO_RESPONSE) == "REAL"

    def test_get_detection_verdict_multimodal_video(self):
        assert ResponseParser.get_detection_verdict(VIDEO_AUDIO_RESPONSE, media="video") == "DEEPFAKE"

    def test_get_detection_verdict_multimodal_audio(self):
        assert ResponseParser.get_detection_verdict(VIDEO_AUDIO_RESPONSE, media="audio") == "DEEPFAKE"

    def test_get_detection_verdict_missing(self):
        assert ResponseParser.get_detection_verdict({}) is None


class TestGetDetectionPercentage:
    """Tests for get_detection_percentage."""

    def test_get_detection_percentage_image_uses_score(self):
        # Images use 'score' instead of 'percentage'
        assert ResponseParser.get_detection_percentage(IMAGE_RESPONSE) == 95

    def test_get_detection_percentage_audio(self):
        assert ResponseParser.get_detection_percentage(AUDIO_RESPONSE) == 87

    def test_get_detection_percentage_video(self):
        assert ResponseParser.get_detection_percentage(VIDEO_RESPONSE) == 92

    def test_get_detection_percentage_multimodal_video(self):
        assert ResponseParser.get_detection_percentage(VIDEO_AUDIO_RESPONSE, media="video") == 82

    def test_get_detection_percentage_multimodal_audio(self):
        assert ResponseParser.get_detection_percentage(VIDEO_AUDIO_RESPONSE, media="audio") == 88

    def test_get_detection_percentage_missing(self):
        assert ResponseParser.get_detection_percentage({}) is None


class TestGetSegments:
    """Tests for get_segments."""

    def test_get_segments_image_empty(self):
        # Images don't have segments
        assert ResponseParser.get_segments(IMAGE_RESPONSE) == []

    def test_get_segments_audio(self):
        segments = ResponseParser.get_segments(AUDIO_RESPONSE)
        assert len(segments) == 2
        assert segments[0]["verdict"] == "DEEPFAKE"
        assert segments[1]["verdict"] == "SUSPICIOUS"

    def test_get_segments_video(self):
        segments = ResponseParser.get_segments(VIDEO_RESPONSE)
        assert len(segments) == 1
        assert segments[0]["score"] == 94

    def test_get_segments_multimodal_video(self):
        segments = ResponseParser.get_segments(VIDEO_AUDIO_RESPONSE, media="video")
        assert segments == []  # No segments in test data

    def test_get_segments_missing(self):
        assert ResponseParser.get_segments({}) == []


class TestFormatDetection:
    """Tests for format_detection."""

    def test_format_detection_image(self):
        result = ResponseParser.format_detection(IMAGE_RESPONSE)
        assert "ResNet50" in result
        assert "v2" in result
        assert "REAL" in result
        assert "95" in result

    def test_format_detection_audio(self):
        result = ResponseParser.format_detection(AUDIO_RESPONSE)
        assert "WaveNet" in result
        assert "v1" in result
        assert "DEEPFAKE" in result
        assert "87" in result

    def test_format_detection_video(self):
        result = ResponseParser.format_detection(VIDEO_RESPONSE)
        assert "FaceForensics" in result
        assert "v3" in result
        assert "REAL" in result
        assert "92" in result

    def test_format_detection_multimodal(self):
        result = ResponseParser.format_detection(VIDEO_AUDIO_RESPONSE, media="video")
        assert "FaceForensics" in result
        assert "DEEPFAKE" in result


class TestFormatSegments:
    """Tests for format_segments."""

    def test_format_segments_image_empty(self):
        result = ResponseParser.format_segments(IMAGE_RESPONSE)
        assert result == []

    def test_format_segments_audio(self):
        result = ResponseParser.format_segments(AUDIO_RESPONSE)
        assert len(result) == 2
        assert "0 -> 5" in result[0]
        assert "DEEPFAKE" in result[0]
        assert "92" in result[0]

    def test_format_segments_video(self):
        result = ResponseParser.format_segments(VIDEO_RESPONSE)
        assert len(result) == 1
        assert "0 -> 10" in result[0]
        assert "REAL" in result[0]
        assert "94" in result[0]

    def test_format_segments_returns_strings(self):
        result = ResponseParser.format_segments(AUDIO_RESPONSE)
        assert all(isinstance(segment, str) for segment in result)


class TestSummarizeBatch:
    """Tests for summarize_batch."""

    def test_summarize_batch_success(self):
        batch = [
            {"file": "image.jpg", "error": None, "result": IMAGE_RESPONSE},
            {"file": "audio.mp3", "error": None, "result": AUDIO_RESPONSE},
        ]
        summaries = ResponseParser.summarize_batch(batch)

        assert len(summaries) == 2
        assert summaries[0]["file"] == "image.jpg"
        assert summaries[0]["verdict"] == "REAL"
        assert summaries[0]["percentage"] == 95
        assert summaries[0]["error"] is None

        assert summaries[1]["file"] == "audio.mp3"
        assert summaries[1]["verdict"] == "DEEPFAKE"
        assert summaries[1]["percentage"] == 87
        assert summaries[1]["error"] is None

    def test_summarize_batch_with_errors(self):
        batch = [
            {"file": "image.jpg", "error": None, "result": IMAGE_RESPONSE},
            {"file": "corrupted.mp4", "error": "File corrupted", "result": None},
        ]
        summaries = ResponseParser.summarize_batch(batch)

        assert len(summaries) == 2
        assert summaries[0]["verdict"] == "REAL"
        assert summaries[0]["error"] is None

        assert summaries[1]["verdict"] == "ERROR"
        assert summaries[1]["percentage"] is None
        assert summaries[1]["error"] == "File corrupted"

    def test_summarize_batch_empty(self):
        summaries = ResponseParser.summarize_batch([])
        assert summaries == []

    def test_summarize_batch_multiple_types(self):
        batch = [
            {"file": "image.jpg", "error": None, "result": IMAGE_RESPONSE},
            {"file": "audio.mp3", "error": None, "result": AUDIO_RESPONSE},
            {"file": "video.mp4", "error": None, "result": VIDEO_RESPONSE},
        ]
        summaries = ResponseParser.summarize_batch(batch)

        assert len(summaries) == 3
        assert summaries[0]["verdict"] == "REAL"
        assert summaries[1]["verdict"] == "DEEPFAKE"
        assert summaries[2]["verdict"] == "REAL"