# OpenResearch flake

Nix packaging for [alphaXiv/OpenResearch](https://github.com/alphaXiv/OpenResearch), using upstream's stable release binaries. Supports `x86_64-linux` and `aarch64-linux`.

## Use at your own risk

This was one-shot with GPT-6.1 Sol lol.

## Usage

In your `flake.nix`

```nix
inputs.openresearch.url = "github:kewin-y/OpenResearch-flake";
```

Somewhere in your config:

```nix
environment.systemPackages = [
    inputs.openresearch.packages.${pkgs.stdenv.hostPlatform.system}.openresearch # OpenResearch desktop app
    inputs.openresearch.packages.${pkgs.stdenv.hostPlatform.system}.orx # orx cli
];
```

## Updates

GitHub Actions checks for the latest stable OpenResearch release and updates the flake inputs daily at **06:23 UTC** (or on manual dispatch). Changes are committed only after builds and CLI checks pass on both supported architectures.

## License

MIT (Same as upstream)
