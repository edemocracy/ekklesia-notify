#!/usr/bin/env -S nix-build -o docker-image-ekklesia-notify.tar
# Run this file: ./docker.nix
# It creates a docker image archive called docker-image-ekklesia-notify.tar.
# Default tag is the git version. You can set a custom tag with:
# ./docker.nix --argstr tag mytag
# Import into docker with:
# docker load -i docker-image-ekklesia-notify.tar
{ sources ? null, tag ? null }:

with builtins;

let
  serveApp = import ./nix/serve_app.nix {
    inherit sources;
    appConfigFile = "/settings.yml";
    listenHost = "0.0.0.0";
    listenPort = "8080";
  };

  deps = import ./nix/deps.nix { inherit sources; };
  inherit (deps) pkgs;
  version = import ./nix/git_version.nix { inherit pkgs; };
  user = "ekklesia-notify";
  passwd = pkgs.writeTextDir "etc/passwd" ''
    ${user}:x:10:10:${user}:/:/noshell
  '';
in

pkgs.dockerTools.buildLayeredImage {
  name = "ekklesia-notify";
  contents = [ passwd ];
  tag =
    if tag == null then
      trace "Automatically tagging image with version ${version}" version
    else
      trace "Tagging image with custom tag '${tag}'" tag;

  config = {
    ExposedPorts = { "8080/tcp" = {}; };
    User = user;
    Entrypoint = [ "${serveApp}/bin/run" ];
    Cmd = [ "# runs uvicorn" ];
  };
}
