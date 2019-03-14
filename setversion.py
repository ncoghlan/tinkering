#!/usr/bin/python3

import pathlib
import re
import shutil

# Ensure any names are legal package names
# From https://packaging.python.org/specifications/core-metadata/#name
ALLOWED_NAMES = re.compile(
    "^([A-Z0-9]|[A-Z0-9][A-Z0-9._-]*[A-Z0-9])$", re.IGNORECASE
)

# Restrict to already normalised package versions
# From https://www.python.org/dev/peps/pep-0440/#appendix-b-parsing-version-strings-with-regular-expressions
ALLOWED_VERSIONS = re.compile(
    r"^([1-9]\d*!)?(0|[1-9]\d*)(\.(0|[1-9]\d*))*((a|b|rc)(0|[1-9]\d*))?(\.post(0|[1-9]\d*))?(\.dev(0|[1-9]\d*))?$"
)

def write_basic_metadata(name, version, target_dir, *, installer="unmanaged"):
    """Writes a basic dist-info directory into the target directory

    - appropriately named dist-info directory
    - METADATA file with name and version details
    - INSTALLER file (default value: "unmanaged")

    RECORD is omitted - if it's required, use a full-fledged installer

    Also deletes any previous metadata directory for the same project name
    """
    # Be strict about permitted metadata to avoid interoperability problems
    name = name.strip()
    if ALLOWED_NAMES.match(name) is None:
        raise ValueError("Invalid package name: {}".format(name))
    version = version.strip()
    if ALLOWED_VERSIONS.match(version) is None:
        raise ValueError("Invalid package version: {}".format(version))

    # Calculate actual metadata contents
    no_hyphen_name = name.replace("-", "_")
    dist_info_dir = "{}-{}.dist-info".format(no_hyphen_name, version)
    metadata = "\n".join((
        "Metadata-Version: 1.0",
        "Name: " + name,
        "Version: " + version,
        "" # Ensure final line is empty
    ))
    installer = installer.strip() + "\n"

    # Remove any old metadata from the target directory
    target_path = pathlib.Path(target_dir).resolve()
    old_metadata_pattern = "{}-*.dist-info".format(name)
    for old_metadata in target_path.glob(old_metadata_pattern):
        shutil.rmtree(old_metadata)

    # Write the new metadata to the target directory
    dist_info_path = target_path / dist_info_dir
    dist_info_path.mkdir()
    metadata_fname = dist_info_path / "METADATA"
    metadata_fname.write_text(metadata)
    installer_fname = dist_info_path / "INSTALLER"
    installer_fname.write_text(installer)


def _main(args=None):
    import sys
    if args is None:
        args = sys.argv
    if len(args) == 4:
        name, version, target_dir = args[1:]
    else:
        msg = "Usage: {} NAME VERSION TARGET_DIR".format(args[0])
        print(msg, file=sys.stderr)
        sys.exit(1)
    write_basic_metadata(name, version, target_dir)

if __name__ == "__main__":
    _main()