import sys
import pathlib
import asyncio

# Ensure the project root is on sys.path
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from cyberette import Cyberette, ResponseParser


# Hardcoded response data
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
    "interpretability": {
        "heatmap": "base64_encoded_heatmap_here",
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
                {"start": 10, "end": 15, "score": 88, "verdict": "DEEPFAKE"},
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
                {"start": 10, "end": 20, "score": 89, "verdict": "REAL"},
            ],
        },
    },
}

VIDEO_AUDIO_RESPONSE = {
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
                "segments": [
                    {"start": 0, "end": 5, "score": 91, "verdict": "DEEPFAKE"},
                    {"start": 5, "end": 10, "score": 84, "verdict": "SUSPICIOUS"},
                ],
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
                "segments": [
                    {"start": 0, "end": 10, "score": 85, "verdict": "DEEPFAKE"},
                    {"start": 10, "end": 20, "score": 79, "verdict": "SUSPICIOUS"},
                ],
            },
        },
    },
}


async def main():
    # Test Image Response
    print("\n" + "=" * 70)
    print("IMAGE RESPONSE")
    print("=" * 70)
    print(f"Model: {ResponseParser.get_model_name(IMAGE_RESPONSE)}")
    print(f"Version: {ResponseParser.get_model_version(IMAGE_RESPONSE)}")
    print(f"Verdict: {ResponseParser.get_detection_verdict(IMAGE_RESPONSE)}")
    print(f"Confidence: {ResponseParser.get_detection_percentage(IMAGE_RESPONSE)}%")
    print(f"Summary: {ResponseParser.format_detection(IMAGE_RESPONSE)}")

    # Test Audio Response
    print("\n" + "=" * 70)
    print("AUDIO RESPONSE")
    print("=" * 70)
    print(f"Model: {ResponseParser.get_model_name(AUDIO_RESPONSE)}")
    print(f"Version: {ResponseParser.get_model_version(AUDIO_RESPONSE)}")
    print(f"Verdict: {ResponseParser.get_detection_verdict(AUDIO_RESPONSE)}")
    print(f"Confidence: {ResponseParser.get_detection_percentage(AUDIO_RESPONSE)}%")
    print(f"Summary: {ResponseParser.format_detection(AUDIO_RESPONSE)}")
    print("\nSegments:")
    for segment_str in ResponseParser.format_segments(AUDIO_RESPONSE):
        print(f"{segment_str}")

    # Test Batch Summary
    print("\n" + "=" * 70)
    print("BATCH PROCESSING")
    print("=" * 70)
    batch_results = [
        {"file": "dog.jpg", "error": None, "result": IMAGE_RESPONSE},
        {"file": "test_audio.mp3", "error": None, "result": AUDIO_RESPONSE},
        {"file": "test_video.mp4", "error": None, "result": VIDEO_RESPONSE},
        {"file": "test_video_audio.mp4", "error": None, "result": VIDEO_AUDIO_RESPONSE},
        {"file": "corrupted.mp4", "error": "File corrupted", "result": None},
    ]

    summaries = ResponseParser.summarize_batch(batch_results)
    for summary in summaries:
        if summary["error"]:
            print(f"{summary['file']:25} | ERROR: {summary['error']}")
        else:
            verdict = summary['verdict'] or "UNKNOWN"
            percentage = summary['percentage'] or 0
            print(
                f"{summary['file']:25} | {verdict:10} | "
                f"Confidence: {percentage}%"
            )

    print("\nAll ResponseParser functions tested successfully!")


if __name__ == "__main__":
    asyncio.run(main())