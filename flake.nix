{
  description = "OpenResearch desktop app and orx CLI for Nix";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs = {nixpkgs, ...}: let
    forAllSystems = nixpkgs.lib.genAttrs [
      "x86_64-linux"
      "aarch64-linux"
    ];
    release = builtins.fromJSON (builtins.readFile ./release.json);

    packagesFor = system: let
      args = {
        pkgs = nixpkgs.legacyPackages.${system};
        inherit release;
      };
    in {
      openresearch = import ./openresearch.nix args;
      orx = import ./orx.nix args;
    };
  in {
    packages = forAllSystems (system: let
      packages = packagesFor system;
    in
      packages // {default = packages.openresearch;});

    checks = forAllSystems (system: let
      pkgs = nixpkgs.legacyPackages.${system};
      packages = packagesFor system;
    in {
      inherit (packages) openresearch orx;
      cli-version = pkgs.runCommand "orx-version-check" {} ''
        ${packages.orx}/bin/orx --version > version.txt
        grep -Fx 'orx ${release.version}' version.txt
        touch "$out"
      '';
    });

    devShells = forAllSystems (system: let
      pkgs = nixpkgs.legacyPackages.${system};
    in {
      default = pkgs.mkShell {
        packages = [pkgs.alejandra pkgs.python3];
      };
    });
  };
}
