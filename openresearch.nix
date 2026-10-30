{
  pkgs,
  release,
}: let
  inherit (pkgs) lib;
  inherit (release) version;
  src = pkgs.fetchurl release.assets.${pkgs.stdenv.hostPlatform.system}.desktop;
  appimageContents = pkgs.appimageTools.extract {
    pname = "openresearch";
    inherit version src;
  };
in
  pkgs.appimageTools.wrapType2 {
    pname = "openresearch";
    inherit version src;
    extraPkgs = pkgs: [pkgs.libgpg-error];
    extraInstallCommands = ''
      install -Dm644 ${appimageContents}/OpenResearch.desktop "$out/share/applications/openresearch.desktop"
      substituteInPlace "$out/share/applications/openresearch.desktop" \
        --replace-fail 'Exec=orx app' "Exec=$out/bin/openresearch" \
        --replace-fail 'Icon=OpenResearch' 'Icon=openresearch'
      install -Dm644 ${appimageContents}/OpenResearch.png "$out/share/icons/hicolor/256x256/apps/openresearch.png"
    '';
    meta = {
      description = "Local-first workspace for research agents";
      homepage = "https://github.com/alphaXiv/OpenResearch";
      license = lib.licenses.mit;
      platforms = ["x86_64-linux" "aarch64-linux"];
      sourceProvenance = [lib.sourceTypes.binaryNativeCode];
      mainProgram = "openresearch";
    };
  }
