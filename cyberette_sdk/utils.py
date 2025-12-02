from typing import Any, List, Dict, Optional


class ResponseParser:
    """Helper class for parsing Cyberette SDK detection responses."""

    @staticmethod
    def safe_get(d: Optional[dict[Any, Any]], keys: list, default=None) -> Any:
        """Traverse a nested dict safely, return default if key path is missing."""
        if d is None or not isinstance(d, dict):
            return default
        for key in keys:
            if not isinstance(d, dict):
                return default
            d = d.get(key, None)
            if d is None:
                return default
        return d

    @staticmethod
    def get_model_name(result: dict, media: str = "main") -> Optional[str]:
        target = result.get(media) if media in ("video", "audio") else result
        return ResponseParser.safe_get(target, ["deepfake", "name"])

    @staticmethod
    def get_model_version(result: dict, media: str = "main") -> Optional[int]:
        target = result.get(media) if media in ("video", "audio") else result
        return ResponseParser.safe_get(target, ["deepfake", "version"])

    @staticmethod
    def get_detection_verdict(result: dict, media: str = "main") -> Optional[str]:
        target = result.get(media) if media in ("video", "audio") else result
        return ResponseParser.safe_get(target, ["deepfake", "detection", "verdict"])

    @staticmethod
    def get_detection_percentage(result: dict, media: str = "main") -> Optional[float]:
        target = result.get(media) if media in ("video", "audio") else result
        # fallback for images where 'score' is used instead of 'percentage'
        return ResponseParser.safe_get(
            target, ["deepfake", "detection", "percentage"]
        ) or ResponseParser.safe_get(target, ["deepfake", "detection", "score"])

    @staticmethod
    def get_segments(result: dict, media: str = "main") -> List[Dict]:
        """Return segments if they exist; empty list otherwise."""
        target = result.get(media) if media in ("video", "audio") else result
        return ResponseParser.safe_get(
            target, ["deepfake", "detection", "segments"], default=[]
        )

    @staticmethod
    def format_detection(result: dict, media: str = "main") -> str:
        """Return a human-readable summary of the detection."""
        verdict = ResponseParser.get_detection_verdict(result, media)
        percentage = ResponseParser.get_detection_percentage(result, media)
        name = ResponseParser.get_model_name(result, media)
        version = ResponseParser.get_model_version(result, media)
        return f"Model: {name} v{version}, Verdict: {verdict} ({percentage}%)"

    @staticmethod
    def format_segments(result: dict, media: str = "main") -> List[str]:
        """Return list of strings describing each segment."""
        segments = ResponseParser.get_segments(result, media)
        formatted = []
        for seg in segments:
            start = seg.get("start")
            end = seg.get("end")
            score = seg.get("score")
            verdict = seg.get("verdict")
            formatted.append(
                f"Segment: {start} -> {end}, Verdict: {verdict} ({score}%)"
            )
        return formatted

    @staticmethod
    def summarize_batch(batch_results: list) -> List[dict]:
        """
        Convert a batch of results into a list of summaries.
        Each summary is a dict: {"file": file_path, "verdict": verdict, "percentage": percentage, "error": error}
        """
        summaries = []

        for r in batch_results:
            if r.get("error") is not None:
                summaries.append(
                    {
                        "file": r.get("file"),
                        "verdict": "ERROR",
                        "percentage": None,
                        "error": r.get("error"),
                    }
                )
            else:
                result = r.get("result", {})
                summaries.append(
                    {
                        "file": r.get("file"),
                        "verdict": ResponseParser.get_detection_verdict(result),
                        "percentage": ResponseParser.get_detection_percentage(result),
                        "error": None,
                    }
                )
        return summaries
