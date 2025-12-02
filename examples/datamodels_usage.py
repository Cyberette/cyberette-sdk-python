"""
Usage examples for Pydantic models in Cyberette SDK.

The models are used for:
1. Type validation - Ensure API responses match expected structure
2. Type hints - Better IDE autocomplete and type checking
3. Serialization - Convert between JSON and Python objects
4. Documentation - Self-documenting code with field descriptions
"""

import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from cyberette import (
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


# ============================================================================
# 1. VALIDATION - Parse and validate API responses
# ============================================================================

def example_image_validation():
    """Validate image response data."""
    print("\n" + "=" * 70)
    print("EXAMPLE 1: Image Response Validation")
    print("=" * 70)

    # Raw API response (dict)
    raw_response = {
        "metadata": None,
        "deepfake": {
            "name": "ResNet50",
            "version": 2,
            "detection": {
                "verdict": "REAL",
                "score": 95,
            },
        },
        "interpretability": {"heatmap": "base64_data"},
    }

    # Parse and validate with Pydantic model
    image = ImageResponse(**raw_response)

    # Now you have type-safe access
    print(f"Model: {image.deepfake.name}")
    print(f"Version: {image.deepfake.version}")
    print(f"Verdict: {image.deepfake.detection.verdict}")
    print(f"Confidence: {image.deepfake.detection.score}%")


def example_audio_validation():
    """Validate audio response with segments."""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Audio Response Validation with Segments")
    print("=" * 70)

    raw_response = {
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

    audio = AudioResponse(**raw_response)

    print(f"Sample Rate: {audio.sample_rate} Hz")
    print(f"Model: {audio.deepfake.name}")
    print(f"Overall Verdict: {audio.deepfake.detection.verdict}")
    print(f"Confidence: {audio.deepfake.detection.percentage}%")
    print(f"\nSegments ({len(audio.deepfake.detection.segments)}):")
    for i, segment in enumerate(audio.deepfake.detection.segments):
        print(f"  Segment {i+1}: {segment.start}s -> {segment.end}s")
        print(f"    Verdict: {segment.verdict}, Score: {segment.score}%")


def example_multimodal_validation():
    """Validate video with both audio and visual tracks."""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Multimodal Video Response Validation")
    print("=" * 70)

    raw_response = {
        "verdict": "DEEPFAKE",
        "percentage": 85,
        "audio": {
            "sample_rate": 44100,
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
            "frame_rate": 24,
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

    video = MultimodalVideoResponse(**raw_response)

    print(f"Overall Verdict: {video.verdict}")
    print(f"Overall Confidence: {video.percentage}%")
    print(f"\nVideo Track:")
    print(f"  Model: {video.video.deepfake.name}")
    print(f"  Verdict: {video.video.deepfake.detection.verdict}")
    print(f"  Confidence: {video.video.deepfake.detection.percentage}%")
    print(f"\nAudio Track:")
    print(f"  Model: {video.audio.deepfake.name}")
    print(f"  Verdict: {video.audio.deepfake.detection.verdict}")
    print(f"  Confidence: {video.audio.deepfake.detection.percentage}%")


# ============================================================================
# 2. TYPE HINTS - Use models for better code documentation
# ============================================================================

def process_detection(response: ImageResponse) -> str:
    """
    Process a detection response.
    Type hint tells you exactly what structure to expect.
    """
    verdict = response.deepfake.detection.verdict
    score = response.deepfake.detection.score
    return f"{verdict} ({score}%)"


def process_batch_results(results: list[BatchResultItem]) -> dict:
    """
    Analyze batch results.
    Type hint shows this is a list of BatchResultItem objects.
    """
    stats = {
        "real": 0,
        "deepfake": 0,
        "suspicious": 0,
        "errors": 0,
    }

    for item in results:
        if item.error:
            stats["errors"] += 1
        elif item.verdict == "REAL":
            stats["real"] += 1
        elif item.verdict == "DEEPFAKE":
            stats["deepfake"] += 1
        elif item.verdict == "SUSPICIOUS":
            stats["suspicious"] += 1

    return stats


def example_type_hints():
    """Demonstrate type hints usage."""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Type Hints for Better Code")
    print("=" * 70)

    # Create an image response
    image = ImageResponse(
        metadata=None,
        deepfake=DeepfakeAnalysis(
            name="ResNet50",
            version=2,
            detection=Detection(verdict="REAL", score=95),
        ),
    )

    # Type-safe function call
    result = process_detection(image)
    print(f"Detection Result: {result}")

    # Batch results
    batch_items = [
        BatchResultItem(
            file="image1.jpg",
            verdict="REAL",
            percentage=95,
            error=None,
        ),
        BatchResultItem(
            file="image2.jpg",
            verdict="DEEPFAKE",
            percentage=87,
            error=None,
        ),
        BatchResultItem(
            file="corrupted.jpg",
            verdict=None,
            percentage=None,
            error="File corrupted",
        ),
    ]

    stats = process_batch_results(batch_items)
    print(f"Batch Statistics: {stats}")


# ============================================================================
# 3. SERIALIZATION - Convert to/from JSON
# ============================================================================

def example_serialization():
    """Demonstrate JSON serialization."""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Serialization to/from JSON")
    print("=" * 70)

    # Create a model
    audio = AudioResponse(
        sample_rate=16000,
        deepfake=DeepfakeAnalysis(
            name="WaveNet",
            version=1,
            detection=Detection(
                verdict="DEEPFAKE",
                percentage=87,
                segments=[
                    Segment(start=0, end=5, score=92, verdict="DEEPFAKE"),
                    Segment(start=5, end=10, score=75, verdict="SUSPICIOUS"),
                ],
            ),
        ),
    )

    # Serialize to JSON string
    json_str = audio.model_dump_json(indent=2)
    print("Serialized to JSON:")
    print(json_str)

    # Parse from JSON string
    parsed = AudioResponse.model_validate_json(json_str)
    print(f"\nDeserialized back to model:")
    print(f"Model: {parsed.deepfake.name}")
    print(f"Verdict: {parsed.deepfake.detection.verdict}")


# ============================================================================
# 4. ERROR HANDLING - Validation errors
# ============================================================================

def example_error_handling():
    """Demonstrate validation errors."""
    print("\n" + "=" * 70)
    print("EXAMPLE 6: Validation Error Handling")
    print("=" * 70)

    # Missing required fields
    try:
        invalid_response = {
            "deepfake": {
                "name": "ResNet50",
                # Missing 'version' and 'detection'
            },
        }
        image = ImageResponse(**invalid_response)
    except Exception as e:
        print(f"Validation Error (caught):")
        print(f"  {type(e).__name__}: {e}")

    # Wrong data type
    try:
        invalid_response = {
            "metadata": None,
            "deepfake": {
                "name": "ResNet50",
                "version": "two",  # Should be int, not string
                "detection": {
                    "verdict": "REAL",
                    "score": 95,
                },
            },
        }
        image = ImageResponse(**invalid_response)
    except Exception as e:
        print(f"\nValidation Error (caught):")
        print(f"  {type(e).__name__}: Invalid version type")


# ============================================================================
# 5. BATCH PROCESSING - Working with BatchResult
# ============================================================================

def example_batch_processing():
    """Demonstrate batch result handling."""
    print("\n" + "=" * 70)
    print("EXAMPLE 7: Batch Processing Results")
    print("=" * 70)

    batch = BatchResult(
        results=[
            BatchResultItem(file="image1.jpg", verdict="REAL", percentage=95),
            BatchResultItem(file="image2.jpg", verdict="DEEPFAKE", percentage=87),
            BatchResultItem(file="corrupted.jpg", error="File corrupted"),
        ],
        total=3,
        successful=2,
        failed=1,
    )

    print(f"Total Files: {batch.total}")
    print(f"Successful: {batch.successful}")
    print(f"Failed: {batch.failed}")
    print(f"\nResults:")
    for item in batch.results:
        if item.error:
            print(f"  {item.file}: ERROR - {item.error}")
        else:
            print(f"  {item.file}: {item.verdict} ({item.percentage}%)")


# ============================================================================
# RUN ALL EXAMPLES
# ============================================================================

if __name__ == "__main__":
    example_image_validation()
    example_audio_validation()
    example_multimodal_validation()
    example_type_hints()
    example_serialization()
    example_error_handling()
    example_batch_processing()

    print("\n" + "=" * 70)
    print("All examples completed!")
    print("=" * 70 + "\n")