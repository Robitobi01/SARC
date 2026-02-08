{ pkgs ? import <nixpkgs> {} }:

pkgs.python313Packages.buildPythonApplication {
  pname = "sarc";
  version = "0.1.0";
  format = "pyproject";
  src = pkgs.lib.cleanSource ./.;

  nativeBuildInputs = [
    pkgs.python313Packages.hatchling
  ];

  propagatedBuildInputs = with pkgs.python313Packages; [
    requests
    cryptography
  ];

  doCheck = false;
}