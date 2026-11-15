# nix-shell, then: python -m sarc -c config.json
{ pkgs ? import <nixpkgs> { } }:
pkgs.mkShell {
  packages = [ (pkgs.python3.withPackages (ps: [ ps.requests ps.cryptography ])) ];
}
