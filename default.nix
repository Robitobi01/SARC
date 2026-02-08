{ pkgs ? import <nixpkgs> {} }:
let
  python = pkgs.python313;
  pyPkgs = python.pkgs;
  src = pkgs.lib.cleanSource ./.;
  sarc = pyPkgs.buildPythonApplication {
    pname = "sarc";
    version = "0.1.0";
    format = "pyproject";
    inherit src;
    nativeBuildInputs = [ pyPkgs.hatchling ];
    propagatedBuildInputs = [ pyPkgs.requests pyPkgs.cryptography ];
    doCheck = false;
  };
in
pkgs.mkShell {
  packages = [ sarc ];
}
