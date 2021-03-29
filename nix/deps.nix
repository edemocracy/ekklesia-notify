{ sources ? null }:
with builtins;

let
  sources_ = if (sources == null) then import ./sources.nix else sources;
  pkgs = import sources_.nixpkgs { };
  niv = (import sources_.niv { }).niv;
  inherit ((import "${sources_.poetry2nix}/overlay.nix") pkgs pkgs) poetry2nix poetry;
  python = pkgs.python38;

  poetryWrapper = with python.pkgs; pkgs.writeScriptBin "poetry" ''
    export PYTHONPATH=
    unset SOURCE_DATE_EPOCH
    ${poetry}/bin/poetry "$@"
  '';

  overrides = poetry2nix.overrides.withDefaults (
    self: super: {
      pykcs11 = super.pykcs11.overrideAttrs (
        old: rec {
          nativeBuildInputs = old.nativeBuildInputs ++ [ pkgs.swig ];
        }
      );

      python-olm = super.python-olm.overrideAttrs (
        old: rec {
          buildInputs = old.buildInputs ++ [ pkgs.olm ];
        }
      );

      oscrypto = super.oscrypto.overrideAttrs (
        old: rec {
          propagatedBuildInputs = old.propagatedBuildInputs ++ [ pkgs.openssl ];
        }
      );
    });

in rec {
  inherit pkgs python;
  inherit (pkgs) lib glibcLocales;
  inherit (python.pkgs) buildPythonApplication;

  mkPoetryApplication = { ... }@args:
    poetry2nix.mkPoetryApplication (args // {
      inherit overrides;
    });

  inherit (poetry2nix.mkPoetryPackages {
    projectDir = ../.;
    inherit python;
    inherit overrides;
  }) poetryPackages pyProject;

  poetryPackagesByName =
    lib.listToAttrs
      (map
        (p: { name = p.pname; value = p; })
        poetryPackages);

  uvicorn = with python.pkgs;
  let
    exportEnv = name: "export ${name}=\${${name}:+\${${name}}:}";

   in pkgs.writeScriptBin "uvicorn" ''
    ${exportEnv "PYTHONPATH"}./src:${pythonPath}
    ${exportEnv "LD_LIBRARY_PATH"}${pkgs.openssl.out}/lib

    ${python.pkgs.uvicorn}/bin/uvicorn "$@"
  '';

  # Can be imported in Python code or run directly as debug tools
  debugLibsAndTools = with python.pkgs; [
    ipython
    poetryPackagesByName.pdbpp
  ];

  pythonDevTest = python.buildEnv.override {
    extraLibs = poetryPackages ++
                debugLibsAndTools;
    ignoreCollisions = true;
  };

  pythonTest = pythonDevTest;
  pythonDev = pythonDevTest;

  # Code style and security tools
  linters = with python.pkgs; let

    # Pylint needs to import the modules of our dependencies
    # but we don't want to override its own PYTHONPATH.
    setSysPath = ''
      import sys
      sys.path.append("${pythonDev}/${pythonDev.sitePackages}")
    '';

    pylintWrapper = with python.pkgs; pkgs.writeScriptBin "pylint" ''
      ${pylint}/bin/pylint --init-hook='${setSysPath}' "$@"
    '';

    isortWrapper = with python.pkgs; pkgs.writeScriptBin "isort" ''
      ${isort}/bin/isort --virtual-env=${pythonDev} "$@"
    '';

  in [
    bandit
    isortWrapper
    mypy
    pylintWrapper
    yapf
  ];

  # Various tools for log files, deps management, running scripts and so on
  shellTools = [
    pkgs.entr
    pkgs.jq
    pkgs.niv
    pkgs.zsh
    poetryPackagesByName.eliot-tree
    poetryWrapper
    uvicorn
  ];


  # Needed for a development nix shell
  shellInputs =
    linters ++
    shellTools ++
    debugLibsAndTools ++ [
      pythonTest
    ];

  pythonPath = "${pythonDevTest}/${pythonDevTest.sitePackages}";
  shellPath = lib.makeBinPath shellInputs;
}
