{ lib, python3Packages }:
python3Packages.buildPythonApplication {
  pname = "sarc";
  version = "0.1.0";
  pyproject = true;

  src = lib.fileset.toSource {
    root = ./.;
    fileset = lib.fileset.unions [
      ./pyproject.toml
      ./README.md
      ./LICENSE
      (lib.fileset.fileFilter (f: f.hasExt "py" || f.name == "config.example.json") ./sarc)
    ];
  };

  build-system = [ python3Packages.hatchling ];
  dependencies = with python3Packages; [ requests cryptography ];
  pythonImportsCheck = [ "sarc" ];

  meta = {
    description = "Stand-alone replay client for Minecraft 1.12.2 (ReplayMod recordings, AFK client)";
    license = lib.licenses.mit;
    mainProgram = "sarc";
  };
}
