import toml


def get_latest_version(changelog_file="changelog.md"):
    latest_major_version = 0
    latest_minor_version = 0
    latest_patch_version = 0
    try:
        with open(changelog_file, "r") as f:
            lines = f.readlines()
            for line in lines:
                if line.startswith("## "):
                    version = line.strip().split(" ")[-1]
                    major_version = int(version.split(".")[0])
                    minor_version = int(version.split(".")[1])
                    patch_version = int(version.split(".")[2])
                    if major_version > latest_major_version:
                        latest_major_version = major_version
                        latest_minor_version = minor_version
                        latest_patch_version = patch_version
                    elif minor_version > latest_minor_version:
                        latest_minor_version = minor_version
                        latest_patch_version = patch_version
                    elif patch_version > latest_patch_version:
                        latest_patch_version = patch_version
                    return
    except FileNotFoundError as exc:
        print(
            f"{type(exc)}: {exc} - {changelog_file} not found. "
            f"Using default version 0.0.0"
        )
    finally:
        return f"{latest_major_version}.{latest_minor_version}.{latest_patch_version}"


def update_pyproject_version(version, pyproject_file="pyproject.toml"):
    with open(pyproject_file, "r") as f:
        pyproject_data = toml.load(f)

    pyproject_data["tool"]["poetry"]["version"] = version

    with open(pyproject_file, "w") as f:
        toml.dump(pyproject_data, f)

    print(f"Updated {pyproject_file} to version {version}")


def main():
    changelog_file = "changelog.md"
    pyproject_file = "pyproject.toml"

    latest_version = get_latest_version(changelog_file)
    update_pyproject_version(latest_version, pyproject_file)


VERSION = get_latest_version()

if __name__ == "__main__":
    main()
