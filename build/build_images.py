#!/usr/bin/env python3
"""Incrementally refresh committed AVIF renditions from editable master images."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE_IMAGES = ROOT / "sources" / "images"
WEB_IMAGES = SOURCE_IMAGES / "avif"
MANIFEST = SOURCE_IMAGES / "avif-manifest.json"
SOURCE_SUFFIXES = {".png", ".jpg", ".jpeg"}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_manifest() -> dict:
    if not MANIFEST.is_file():
        return {"version": 1, "format": "avif", "files": {}}
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def save_manifest(manifest: dict) -> None:
    temporary = MANIFEST.with_suffix(".json.tmp")
    temporary.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    temporary.replace(MANIFEST)


def encode_with_sips(source: Path, destination: Path, quality: int) -> None:
    if not shutil.which("sips"):
        raise RuntimeError(
            "The incremental image builder currently requires macOS `sips`. "
            "The normal book build remains platform independent."
        )
    with tempfile.TemporaryDirectory(prefix="lakokonyv-avif-") as directory:
        temporary = Path(directory) / destination.name
        subprocess.run(
            [
                "sips", "-s", "format", "avif", "-s", "formatOptions",
                str(quality), str(source), "--out", str(temporary),
            ],
            check=True,
            stdout=subprocess.DEVNULL,
        )
        temporary.replace(destination)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--quality", type=int, default=60,
        help="AVIF quality for newly encoded images (default: 60)",
    )
    parser.add_argument(
        "--force", action="store_true", help="Re-encode every image",
    )
    parser.add_argument(
        "--adopt-existing", action="store_true",
        help="Register existing AVIF files without re-encoding them",
    )
    args = parser.parse_args()
    if not 0 <= args.quality <= 100:
        parser.error("--quality must be between 0 and 100")

    sources = sorted(
        path for path in SOURCE_IMAGES.iterdir()
        if path.is_file() and path.suffix.lower() in SOURCE_SUFFIXES
    )
    stems = [path.stem for path in sources]
    if len(stems) != len(set(stems)):
        raise ValueError("Master image filenames must have unique stems")

    WEB_IMAGES.mkdir(exist_ok=True)
    manifest = load_manifest()
    records = manifest.setdefault("files", {})
    encoded = adopted = unchanged = 0

    for source in sources:
        destination = WEB_IMAGES / f"{source.stem}.avif"
        source_hash = sha256(source)
        record = records.get(source.name, {})
        current = (
            destination.is_file()
            and record.get("source_sha256") == source_hash
            and record.get("output_sha256") == sha256(destination)
        )
        if current and not args.force:
            unchanged += 1
            continue
        if args.adopt_existing and destination.is_file() and not args.force:
            adopted += 1
        else:
            encode_with_sips(source, destination, args.quality)
            encoded += 1
        records[source.name] = {
            "output": destination.name,
            "output_sha256": sha256(destination),
            "source_sha256": source_hash,
        }

    source_names = {path.name for path in sources}
    for obsolete in set(records) - source_names:
        del records[obsolete]
    manifest.update({"version": 1, "format": "avif", "quality": args.quality})
    save_manifest(manifest)
    print(
        f"AVIF images: {encoded} encoded, {adopted} adopted, "
        f"{unchanged} unchanged; {len(sources)} total."
    )


if __name__ == "__main__":
    main()
