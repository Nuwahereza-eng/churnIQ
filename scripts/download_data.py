"""Download the IBM Telco Customer Churn dataset into data/raw/.

Usage:
    python scripts/download_data.py [--force]

If you have no internet access, download the file manually from
https://github.com/IBM/telco-customer-churn-on-icp4d/blob/master/data/Telco-Customer-Churn.csv
(use the "Download raw file" button) and save it as data/raw/Telco-Customer-Churn.csv.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config import RAW_DATA_PATH  # noqa: E402
from src.data_acquisition import download_dataset  # noqa: E402
from src.data_loader import file_sha256  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Download the IBM Telco Customer Churn dataset.")
    parser.add_argument("--force", action="store_true", help="re-download even if the file exists")
    args = parser.parse_args()
    if RAW_DATA_PATH.exists() and not args.force:
        print(f"Dataset already present at {RAW_DATA_PATH.relative_to(ROOT)} (use --force to re-download).")
        return
    try:
        path = download_dataset(force=args.force)
    except OSError as exc:
        print(f"Download failed: {exc}", file=sys.stderr)
        print("Download the CSV manually (see data/README.md) and save it as "
              f"{RAW_DATA_PATH.relative_to(ROOT)}", file=sys.stderr)
        sys.exit(1)
    print(f"Saved {path.relative_to(ROOT)} ({path.stat().st_size:,} bytes, sha256 {file_sha256(path)[:16]}...)")


if __name__ == "__main__":
    main()
