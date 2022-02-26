#!/usr/bin/env -S nix-build -o serve_app
{ sources ? null,
  appConfigFile ? null,
  listenHost ? "127.0.0.1",
  listenPort ? "8080",
  system ? builtins.currentSystem
}:
let
  ekklesia-notify = import ../. { inherit sources system; };
  inherit (ekklesia-notify) dependencyEnv deps src;
  inherit (deps) pkgs uvicorn lib;
  pythonpath = "${dependencyEnv}/${dependencyEnv.sitePackages}";

  exportConfigEnvVar =
    lib.optionalString
      (appConfigFile != null)
      "export EKKLESIA_NOTIFY_CONFIG=\${EKKLESIA_NOTIFY_CONFIG:-${appConfigFile}}";

  runUvicorn = pkgs.writeShellScriptBin "run" ''
    ${exportConfigEnvVar}
    cd ${src}
    ${uvicorn}/bin/uvicorn ekklesia_notify.main:app --host ${listenHost} --port ${listenPort}
  '';

in pkgs.buildEnv {
  name = "ekklesia-notify-serve-app";
  paths = [ runUvicorn ];
}
