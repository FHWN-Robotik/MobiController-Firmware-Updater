{ pkgs ? import <nixpkgs> { } }:

let
  pythonEnv = pkgs.python3.withPackages
    (p: with p; [
      requests
      packaging
      tqdm
    ]);

in
pkgs.mkShell
{
  nativeBuildInputs = with pkgs; [
    pythonEnv
    dfu-util
  ];
}
