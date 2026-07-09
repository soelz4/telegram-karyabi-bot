{ pkgs ? import <nixpkgs> {} }:

pkgs.mkShell {
  packages = [
    pkgs.python314
    pkgs.libxml2
    pkgs.libxslt
    pkgs.pkg-config
    pkgs.zlib
    pkgs.gcc
    pkgs.tree
    pkgs.stdenv.cc.cc.lib
  ];

  shellHook = ''
    echo "Python 3.14 Development Shell"

    export LD_LIBRARY_PATH=${
      pkgs.lib.makeLibraryPath [
        pkgs.libxml2
        pkgs.libxslt
        pkgs.zlib
        pkgs.stdenv.cc.cc.lib
      ]
    }:$LD_LIBRARY_PATH
  '';
}
