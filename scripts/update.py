#!/usr/bin/env python3
"""Pin the latest stable OpenResearch Linux release and verify its downloads."""

import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request


ROOT = Path(__file__).resolve().parent.parent
RELEASE_FILE = ROOT / "release.json"
REPOSITORY = "https://github.com/alphaXiv/OpenResearch"
API_URL = "https://api.github.com/repos/alphaXiv/OpenResearch/releases/latest"


class NoAPIRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # Never forward the API token to a redirect destination.
        raise ValueError("Unexpected redirect from the GitHub release API")


def latest_release():
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "OpenResearch-flake-updater",
    }
    if token := os.environ.get("GITHUB_TOKEN"):
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(API_URL, headers=headers)
    opener = urllib.request.build_opener(NoAPIRedirect())
    with opener.open(request, timeout=60) as response:
        release = json.load(response)
    if release.get("draft") or release.get("prerelease"):
        raise ValueError("The latest release is not stable")
    return release


def verified_asset(asset, expected_url):
    name = asset["name"]
    digest = asset.get("digest")
    if not isinstance(digest, str) or not re.fullmatch(r"sha256:[0-9a-fA-F]{64}", digest):
        raise ValueError(f"{name}: GitHub must provide a usable SHA-256 digest")
    if asset["browser_download_url"] != expected_url:
        raise ValueError(f"{name}: unexpected release download URL")

    print(f"Verifying {name}", flush=True)
    sha256 = hashlib.sha256()
    # A separate, unauthenticated request keeps credentials off asset hosts.
    with urllib.request.urlopen(expected_url, timeout=120) as response:
        while chunk := response.read(1024 * 1024):
            sha256.update(chunk)
    if sha256.hexdigest() != digest.split(":", 1)[1].lower():
        raise ValueError(f"{name}: download does not match the GitHub SHA-256 digest")
    return {
        "url": expected_url,
        "hash": "sha256-" + base64.b64encode(sha256.digest()).decode("ascii"),
    }


def proposed_release():
    release = latest_release()
    tag = release["tag_name"]
    version = tag.removeprefix("v")
    if not version:
        raise ValueError("The release tag has no version")
    assets = {asset["name"]: asset for asset in release["assets"]}
    result = {"version": version, "tag": tag, "assets": {}}
    for arch in ("x86_64", "aarch64"):
        result["assets"][f"{arch}-linux"] = {}
        names = {
            "desktop": f"OpenResearch-{arch}.AppImage",
            "cli": f"openresearch-cli-{arch}-unknown-linux-musl.tar.xz",
        }
        for kind, name in names.items():
            if name not in assets:
                raise ValueError(f"The latest release is missing {name}")
            url = f"{REPOSITORY}/releases/download/{urllib.parse.quote(tag, safe='')}/{name}"
            result["assets"][f"{arch}-linux"][kind] = verified_asset(assets[name], url)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="exit 1 if metadata differs; do not write")
    args = parser.parse_args()
    proposed = proposed_release()
    current = json.loads(RELEASE_FILE.read_text()) if RELEASE_FILE.exists() else None
    if current == proposed:
        print("release.json is up to date")
        return 0
    if args.check:
        print("release.json needs updating")
        return 1

    # Only replace metadata after all four downloads have been verified.
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=ROOT, delete=False) as handle:
            temporary = Path(handle.name)
            handle.write(json.dumps(proposed, indent=2) + "\n")
        temporary.replace(RELEASE_FILE)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    print(f"Updated release.json to {proposed['tag']}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, KeyError, urllib.error.URLError) as error:
        print(f"Update failed: {error}", file=sys.stderr)
        sys.exit(1)
