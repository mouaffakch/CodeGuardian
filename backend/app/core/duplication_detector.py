import hashlib
from typing import List, Dict, Any, Tuple
from collections import defaultdict
from app.config import settings

class DuplicationDetector:
    """Detects duplicated code blocks across multiple files using rolling block hashing."""

    def __init__(self, min_lines: int = None):
        self.min_lines = min_lines or settings.min_duplication_lines

    def find_duplications(self, file_contents: Dict[str, str]) -> Dict[str, Any]:
        """
        Takes a mapping of file_path -> file_content.
        Returns detected duplicate blocks, total duplicate lines, and duplication percentage.
        """
        processed_files: Dict[str, List[Tuple[int, str]]] = {}
        total_code_lines = 0

        for file_path, content in file_contents.items():
            lines = content.splitlines()
            total_code_lines += len(lines)
            normalized = []
            for idx, line in enumerate(lines, 1):
                clean = line.strip()
                if not clean or clean.startswith(("#", "//", "/*", "*")):
                    continue
                normalized.append((idx, clean))
            processed_files[file_path] = normalized

        if not processed_files:
            return {"blocks": [], "total_duplicate_lines": 0, "duplication_percentage": 0.0}

        window_size = self.min_lines
        block_occurrences = defaultdict(list)

        for file_path, norm_lines in processed_files.items():
            if len(norm_lines) < window_size:
                continue

            for i in range(len(norm_lines) - window_size + 1):
                window = norm_lines[i : i + window_size]
                text_block = "\n".join(item[1] for item in window)
                block_hash = hashlib.sha256(text_block.encode("utf-8")).hexdigest()[:16]
                start_line = window[0][0]
                end_line = window[-1][0]
                block_occurrences[block_hash].append((file_path, start_line, end_line, i, text_block))

        raw_clones = []
        for b_hash, occurrences in block_occurrences.items():
            if len(occurrences) > 1:
                for i in range(len(occurrences)):
                    for j in range(i + 1, len(occurrences)):
                        occ_a = occurrences[i]
                        occ_b = occurrences[j]
                        if occ_a[0] == occ_b[0] and abs(occ_a[1] - occ_b[1]) < window_size:
                            continue
                        raw_clones.append({
                            "hash": b_hash,
                            "file_a": occ_a[0],
                            "start_line_a": occ_a[1],
                            "end_line_a": occ_a[2],
                            "file_b": occ_b[0],
                            "start_line_b": occ_b[1],
                            "end_line_b": occ_b[2],
                            "line_count": window_size,
                            "snippet": occ_a[4]
                        })

        merged_clones = self._merge_clones(raw_clones)
        
        duplicated_lines_set = set()
        for clone in merged_clones:
            for line in range(clone["start_line_a"], clone["end_line_a"] + 1):
                duplicated_lines_set.add((clone["file_a"], line))
            for line in range(clone["start_line_b"], clone["end_line_b"] + 1):
                duplicated_lines_set.add((clone["file_b"], line))

        total_dup_lines = len(duplicated_lines_set)
        dup_pct = round((total_dup_lines / max(1, total_code_lines)) * 100, 2)

        return {
            "blocks": merged_clones,
            "total_duplicate_lines": total_dup_lines,
            "duplication_percentage": min(100.0, dup_pct)
        }

    def _merge_clones(self, clones: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Merges adjacent duplicate windows to avoid fragmenting."""
        if not clones:
            return []

        sorted_clones = sorted(
            clones,
            key=lambda c: (c["file_a"], c["file_b"], c["start_line_a"], c["start_line_b"])
        )

        merged = []
        current = sorted_clones[0].copy()

        for next_c in sorted_clones[1:]:
            same_pair = (current["file_a"] == next_c["file_a"] and current["file_b"] == next_c["file_b"])
            overlaps = (next_c["start_line_a"] <= current["end_line_a"] + 2 and
                        next_c["start_line_b"] <= current["end_line_b"] + 2)

            if same_pair and overlaps:
                current["end_line_a"] = max(current["end_line_a"], next_c["end_line_a"])
                current["end_line_b"] = max(current["end_line_b"], next_c["end_line_b"])
                current["line_count"] = current["end_line_a"] - current["start_line_a"] + 1
            else:
                merged.append(current)
                current = next_c.copy()

        merged.append(current)
        return merged

duplication_detector = DuplicationDetector()
