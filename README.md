# OpenResearch flake

Nix packaging for [alphaXiv/OpenResearch](https://github.com/alphaXiv/OpenResearch), using upstream's stable release binaries. Supports `x86_64-linux` and `aarch64-linux`.

## Run

From this directory, with Nix flakes enabled:

```sh
# Desktop app (also includes an applications-menu entry when installed)
nix run .

# Standalone CLI; opens the dashboard in your browser
nix run .#orx -- up

# Build either package
nix build .#openresearch
nix build .#orx

# Install into your profile
nix profile add .#openresearch .#orx
```

The default package is `openresearch`. The separate `orx` package is the static CLI, not a shell alias for the desktop launcher. The desktop uses Nixpkgs' AppImage FHS wrapper and does not require FUSE; Linux user namespaces must be available. The bundled GUI currently uses XWayland on Wayland desktops.

After publishing this repository as `kewin-y/OpenResearch-flake`, add it to a NixOS or Home Manager flake:

```nix
inputs.openresearch = {
  url = "github:kewin-y/OpenResearch-flake";
  inputs.nixpkgs.follows = "nixpkgs";
};
```

Then, in a module receiving `inputs` through `specialArgs` (or `extraSpecialArgs` for Home Manager):

```nix
environment.systemPackages = [
  inputs.openresearch.packages.${pkgs.stdenv.hostPlatform.system}.openresearch
  inputs.openresearch.packages.${pkgs.stdenv.hostPlatform.system}.orx
];
```

For Home Manager, use `home.packages` instead of `environment.systemPackages`. Consumers following a different Nixpkgs revision use that revision rather than the one verified here.

## Automatic updates

`.github/workflows/update.yml` runs daily at **06:23 UTC** and can be dispatched manually on the default branch. It:

1. Finds the latest stable upstream release.
2. Downloads all four Linux desktop/CLI assets and verifies each against GitHub's published SHA-256 digest.
3. Updates `release.json` and runs `nix flake update` to refresh `flake.lock`.
4. Builds both packages and runs the flake checks and CLI version smoke check on native x86-64 and ARM64 runners.
5. Commits only the two metadata files after both runners succeed. If the default branch moved during verification, it refuses the stale update rather than overwriting changes.

Unchanged proposals do not produce commits. Missing assets, missing digests, checksum mismatches, or failed builds stop the update. Pushes and pull requests run the same native build/CLI checks through `.github/workflows/check.yml`.

To activate automation, commit and push these files to a GitHub repository with Actions enabled. The update job uses the built-in `GITHUB_TOKEN`; no personal access token is needed. Repository/organization policy must permit the job's `contents: write` permission and bot pushes to the default branch. Branch protection that requires pull requests needs an appropriate bot exemption. Native `ubuntu-24.04-arm` runners must be available to the repository.

GitHub suppresses workflow triggers from bot-token pushes, so the updater verifies its own proposed changes before committing. Your consuming flake remains pinned: run `nix flake update openresearch` there to pick up a new packaging revision.

## Manual maintenance

Package definitions live separately in `openresearch.nix` (desktop) and `orx.nix` (CLI).

```sh
nix develop
python3 scripts/update.py          # Download, verify, and pin the latest release
python3 scripts/update.py --check  # Verify downloads without writing; exit 1 if metadata differs
nix flake update
nix flake check
nix run .#orx -- --version
nix fmt -- flake.nix openresearch.nix orx.nix
```

The updater uses Python's standard library. `GITHUB_TOKEN` is optional for local runs and is sent only to the GitHub API, never to release download hosts. If you initialize a Git repository, add all flake/package/metadata files to Git before evaluating the flake; Nix excludes untracked files from Git flakes.

## Notes

- This wraps upstream binaries; it is not a source build. Versions, asset URLs and SHA-256 hashes are pinned in `release.json`, with Nixpkgs pinned in `flake.lock`.
- Update through Nix, not OpenResearch's in-app/CLI self-updater: installed files live in the read-only Nix store.
- Coding agents and compute tools are not bundled. Install the integrations you use separately.
- Upstream release builds enable opt-out usage analytics. Disable them in Settings or with `orx telemetry off` (for example, `nix run .#orx -- telemetry off`). See the [upstream privacy description](https://github.com/alphaXiv/OpenResearch#usage-analytics).
- Desktop rendering was smoke-tested on x86-64 Linux using an isolated Xvfb session. ARM64 was evaluated locally and is configured to build in the native CI matrix; local ARM64 execution and hosted Actions execution have not been verified here.
