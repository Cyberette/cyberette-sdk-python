"""Unit tests for cyberette.models Pydantic models."""
import pytest
from pydantic import ValidationError
from cyberette_sdk.models import (
    Segment,
    Detection,
    DeepfakeAnalysis,
    ImageResponse,
    AudioResponse,
    VideoResponse,
    MultimodalVideoResponse,
    BatchResultItem,
    BatchResult,
    ErrorResponse,
)


class TestSegment:
    """Tests for Segment model."""

    def test_segment_valid(self):
        segment = Segment(start=0, end=5, score=92, verdict="DEEPFAKE")
        assert segment.start == 0
        assert segment.end == 5
        assert segment.score == 92
        assert segment.verdict == "DEEPFAKE"

    def test_segment_missing_required_field(self):
        with pytest.raises(ValidationError):
            Segment(start=0, end=5, score=92)  # Missing verdict

    def test_segment_invalid_type(self):
        with pytest.raises(ValidationError):
            Segment(start="zero", end=5, score=92, verdict="DEEPFAKE")


class TestDetection:
    """Tests for Detection model."""

    def test_detection_valid_minimal(self):
        detection = Detection(verdict="REAL")
        assert detection.verdict == "REAL"
        assert detection.percentage is None
        assert detection.score is None
        assert detection.segments == []

    def test_detection_with_percentage(self):
        detection = Detection(verdict="DEEPFAKE", percentage=87)
        assert detection.verdict == "DEEPFAKE"
        assert detection.percentage == 87

    def test_detection_with_score(self):
        detection = Detection(verdict="REAL", score=95)
        assert detection.score == 95

    def test_detection_with_segments(self):
        segments = [
            Segment(start=0, end=5, score=92, verdict="DEEPFAKE"),
            Segment(start=5, end=10, score=75, verdict="SUSPICIOUS"),
        ]
        detection = Detection(verdict="DEEPFAKE", percentage=87, segments=segments)
        assert len(detection.segments) == 2
        assert detection.segments[0].verdict == "DEEPFAKE"

    def test_detection_missing_verdict(self):
        with pytest.raises(ValidationError):
            Detection(percentage=87)


class TestDeepfakeAnalysis:
    """Tests for DeepfakeAnalysis model."""

    def test_deepfake_analysis_valid(self):
        analysis = DeepfakeAnalysis(
            name="ResNet50",
            version=2,
            detection=Detection(verdict="REAL", score=95),
        )
        assert analysis.name == "ResNet50"
        assert analysis.version == 2
        assert analysis.detection.verdict == "REAL"

    def test_deepfake_analysis_missing_name(self):
        with pytest.raises(ValidationError):
            DeepfakeAnalysis(
                version=2,
                detection=Detection(verdict="REAL", score=95),
            )

    def test_deepfake_analysis_invalid_version_type(self):
        with pytest.raises(ValidationError):
            DeepfakeAnalysis(
                name="ResNet50",
                version="two",  # Should be int
                detection=Detection(verdict="REAL", score=95),
            )


class TestImageResponse:
    """Tests for ImageResponse model."""

    def test_image_response_valid(self):
        response = ImageResponse(
            metadata=None,
            deepfake=DeepfakeAnalysis(
                name="ResNet50",
                version=2,
                detection=Detection(verdict="REAL", score=95),
            ),
            interpretability={"heatmap": "base64_data"},
        )
        assert response.deepfake.name == "ResNet50"
        assert response.deepfake.detection.verdict == "REAL"

    def test_image_response_missing_deepfake(self):
        with pytest.raises(ValidationError):
            ImageResponse(metadata=None, interpretability=None)

    def test_image_response_from_dict(self):
        data = {
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
        response = ImageResponse(**data)
        assert response.deepfake.name == "ResNet50"


class TestAudioResponse:
    """Tests for AudioResponse model."""

    def test_audio_response_valid(self):
        response = AudioResponse(
            sample_rate=16000,
            deepfake=DeepfakeAnalysis(
                name="WaveNet",
                version=1,
                detection=Detection(verdict="DEEPFAKE", percentage=87),
            ),
        )
        assert response.sample_rate == 16000
        assert response.deepfake.name == "WaveNet"

    def test_audio_response_with_segments(self):
        response = AudioResponse(
            sample_rate=16000,
            deepfake=DeepfakeAnalysis(
                name="WaveNet",
                version=1,
                detection=Detection(
                    verdict="DEEPFAKE",
                    percentage=87,
                    segments=[
                        Segment(start=0, end=5, score=92, verdict="DEEPFAKE"),
                    ],
                ),
            ),
        )
        assert len(response.deepfake.detection.segments) == 1

    def test_audio_response_missing_sample_rate(self):
        with pytest.raises(ValidationError):
            AudioResponse(
                deepfake=DeepfakeAnalysis(
                    name="WaveNet",
                    version=1,
                    detection=Detection(verdict="DEEPFAKE", percentage=87),
                ),
            )


class TestVideoResponse:
    """Tests for VideoResponse model."""

    def test_video_response_valid(self):
        response = VideoResponse(
            frame_rate=30,
            deepfake=DeepfakeAnalysis(
                name="FaceForensics",
                version=3,
                detection=Detection(verdict="REAL", percentage=92),
            ),
        )
        assert response.frame_rate == 30
        assert response.deepfake.name == "FaceForensics"

    def test_video_response_missing_frame_rate(self):
        with pytest.raises(ValidationError):
            VideoResponse(
                deepfake=DeepfakeAnalysis(
                    name="FaceForensics",
                    version=3,
                    detection=Detection(verdict="REAL", percentage=92),
                ),
            )


class TestMultimodalVideoResponse:
    """Tests for MultimodalVideoResponse model."""

    def test_multimodal_video_response_valid(self):
        response = MultimodalVideoResponse(
            verdict="DEEPFAKE",
            percentage=85,
            audio=AudioResponse(
                sample_rate=44100,
                deepfake=DeepfakeAnalysis(
                    name="WaveNet",
                    version=1,
                    detection=Detection(verdict="DEEPFAKE", percentage=88),
                ),
            ),
            video=VideoResponse(
                frame_rate=24,
                deepfake=DeepfakeAnalysis(
                    name="FaceForensics",
                    version=3,
                    detection=Detection(verdict="DEEPFAKE", percentage=82),
                ),
            ),
        )
        assert response.verdict == "DEEPFAKE"
        assert response.percentage == 85
        assert response.audio.deepfake.name == "WaveNet"
        assert response.video.deepfake.name == "FaceForensics"

    def test_multimodal_video_response_missing_audio(self):
        with pytest.raises(ValidationError):
            MultimodalVideoResponse(
                verdict="DEEPFAKE",
                percentage=85,
                video=VideoResponse(
                    frame_rate=24,
                    deepfake=DeepfakeAnalysis(
                        name="FaceForensics",
                        version=3,
                        detection=Detection(verdict="DEEPFAKE", percentage=82),
                    ),
                ),
            )


class TestBatchResultItem:
    """Tests for BatchResultItem model."""

    def test_batch_result_item_success(self):
        item = BatchResultItem(
            file="image.jpg",
            verdict="REAL",
            percentage=95,
            error=None,
        )
        assert item.file == "image.jpg"
        assert item.verdict == "REAL"
        assert item.percentage == 95
        assert item.error is None

    def test_batch_result_item_with_error(self):
        item = BatchResultItem(
            file="corrupted.jpg",
            verdict=None,
            percentage=None,
            error="File corrupted",
        )
        assert item.error == "File corrupted"
        assert item.verdict is None

    def test_batch_result_item_missing_file(self):
        with pytest.raises(ValidationError):
            BatchResultItem(verdict="REAL", percentage=95)


class TestBatchResult:
    """Tests for BatchResult model."""

    def test_batch_result_valid(self):
        batch = BatchResult(
            results=[
                BatchResultItem(file="image1.jpg", verdict="REAL", percentage=95),
                BatchResultItem(file="image2.jpg", verdict="DEEPFAKE", percentage=87),
            ],
            total=2,
            successful=2,
            failed=0,
        )
        assert len(batch.results) == 2
        assert batch.total == 2
        assert batch.successful == 2
        assert batch.failed == 0

    def test_batch_result_empty_results(self):
        batch = BatchResult(
            results=[],
            total=0,
            successful=0,
            failed=0,
        )
        assert len(batch.results) == 0

    def test_batch_result_with_errors(self):
        batch = BatchResult(
            results=[
                BatchResultItem(file="image1.jpg", verdict="REAL", percentage=95),
                BatchResultItem(
                    file="corrupted.jpg",
                    verdict=None,
                    percentage=None,
                    error="File corrupted",
                ),
            ],
            total=2,
            successful=1,
            failed=1,
        )
        assert batch.failed == 1


class TestErrorResponse:
    """Tests for ErrorResponse model."""

    def test_error_response_valid(self):
        error = ErrorResponse(
            error="File not found",
            code="FILE_NOT_FOUND",
            details={"file_path": "path/to/file.mp4"},
        )
        assert error.error == "File not found"
        assert error.code == "FILE_NOT_FOUND"
        assert error.details["file_path"] == "path/to/file.mp4"

    def test_error_response_no_details(self):
        error = ErrorResponse(
            error="Network error",
            code="NETWORK_ERROR",
        )
        assert error.error == "Network error"
        assert error.details is None

    def test_error_response_missing_code(self):
        with pytest.raises(ValidationError):
            ErrorResponse(error="File not found")


class TestSerialization:
    """Tests for model serialization/deserialization."""

    def test_image_response_serialization(self):
        response = ImageResponse(
            metadata=None,
            deepfake=DeepfakeAnalysis(
                name="ResNet50",
                version=2,
                detection=Detection(verdict="REAL", score=95),
            ),
        )
        json_str = response.model_dump_json()
        assert "ResNet50" in json_str
        assert "REAL" in json_str

    def test_image_response_deserialization(self):
        json_str = """{
            "metadata": null,
            "deepfake": {
                "name": "ResNet50",
                "version": 2,
                "detection": {
                    "verdict": "REAL",
                    "percentage": null,
                    "score": 95,
                    "segments": []
                }
            },
            "interpretability": null
        }"""
        response = ImageResponse.model_validate_json(json_str)
        assert response.deepfake.name == "ResNet50"
        assert response.deepfake.detection.verdict == "REAL"

    def test_audio_response_serialization(self):
        response = AudioResponse(
            sample_rate=16000,
            deepfake=DeepfakeAnalysis(
                name="WaveNet",
                version=1,
                detection=Detection(
                    verdict="DEEPFAKE",
                    percentage=87,
                    segments=[
                        Segment(start=0, end=5, score=92, verdict="DEEPFAKE"),
                    ],
                ),
            ),
        )
        json_str = response.model_dump_json()
        assert "16000" in json_str
        assert "WaveNet" in json_str