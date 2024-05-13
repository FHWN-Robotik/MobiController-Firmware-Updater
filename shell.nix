{ pkgs ? import <nixpkgs> { } }:

let
  pythonEnv = pkgs.python3.withPackages
    (p: with p; [
      requests
      tqdm
    ]);

in
pkgs.mkShell
{
  nativeBuildInputs = with pkgs; [
    pythonEnv
    dfu-util
    pipreqs
  ];
}
