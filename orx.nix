{
  pkgs,
  release,
}: let
  inherit (pkgs) lib;
in
  pkgs.stdenvNoCC.mkDerivation {
    pname = "orx";
    inherit (release) version;
    src = pkgs.fetchurl release.assets.${pkgs.stdenv.hostPlatform.system}.cli;
    dontConfigure = true;
    dontBuild = true;
    dontStrip = true;
    installPhase = ''
      runHook preInstall
      install -Dm755 orx "$out/bin/orx"
      runHook postInstall
    '';
    meta = {
      description = "OpenResearch command-line research agent workspace";
      homepage = "https://github.com/alphaXiv/OpenResearch";
      license = lib.licenses.mit;
      platforms = ["x86_64-linux" "aarch64-linux"];
      sourceProvenance = [lib.sourceTypes.binaryNativeCode];
      mainProgram = "orx";
    };
  }
