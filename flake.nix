{
  description = "Dev environment for hugo & hinode";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }: 
    flake-utils.lib.eachDefaultSystem
      (system:
        let
         pkgs = import nixpkgs { inherit system; };
        in {
          devShells.default = (pkgs.buildFHSUserEnv {
            name = "Devshell";
            runScript = "fish";
            targetPkgs = pkgs: (with pkgs;[
              nodejs_20
              go
              dart-sass
            ]);
          }).env;
        }
      );
}
