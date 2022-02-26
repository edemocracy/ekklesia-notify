# Build Python package.
# Can be installed in the current user profile with:
# nix-env -if .
{ sources ? null, system ? builtins.currentSystem }:
let
  deps = import ./nix/deps.nix { inherit sources; };
  inherit (deps) pkgs mkPoetryApplication python pyProject;
  inherit (deps.pyProject) version;
  src = pkgs.nix-gitignore.gitignoreSource [] ./.;

in mkPoetryApplication {
  doCheck = false;
  projectDir = ./.;
  inherit python src version;

  passthru = {
    inherit deps src version;
  };
}
