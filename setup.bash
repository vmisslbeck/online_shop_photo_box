#!/usr/bin/env bash

# One-time setup script for this project.
# The script will skip all work if `gphoto2` is already installed.

# Ensure we're running under bash. Many features used in this script
# (e.g. [[ ... ]], pushd/popd, local, source) are bash-specific and
# will fail under `/bin/sh` on many systems (dash on Debian/Ubuntu).
if [ -z "${BASH_VERSION:-}" ]; then
	if command -v bash >/dev/null 2>&1; then
		exec bash "$0" "$@"
	else
		echo "This script requires bash. Please run with 'bash ./setup.bash' or install bash." >&2
		exit 1
	fi
fi

# NOTE (English comments):
# - We try to build libgphoto2 and gphoto2 from upstream sources first
#   (this allows newer versions). If that fails we fall back to package
#   manager installations (apt) where available.
# - We install platform-specific `python3-tk` only when the OS/distro
#   indicates it is appropriate.

if command -v gphoto2 >/dev/null 2>&1; then
	echo "gphoto2 is already installed. Will skip building/installing libgphoto2 and gphoto2."
	GPHOTO_PRESENT=1
else
	GPHOTO_PRESENT=0
fi

OS_NAME=$(uname)
ID=""
ID_LIKE=""
if [[ "$OS_NAME" == "Linux" ]] && [[ -f /etc/os-release ]]; then
	. /etc/os-release
fi

# Install common build dependencies on Debian/Ubuntu-like systems when
# building from source. This includes `libpopt-dev` which is required
# by libgphoto2 (you mentioned you had to install it).
install_build_deps() {
	if command -v apt-get >/dev/null 2>&1; then
		echo "Installing common build dependencies for source build (apt)"
		sudo apt-get update || true
		sudo apt-get install -y build-essential libusb-1.0-0-dev libpopt-dev libtool pkg-config autoconf automake gettext || \
			echo "Some build-deps failed to install; you may need to install them manually (e.g. libpopt-dev)"
	else
		echo "apt-get not available; skipping automatic install of build-deps"
	fi
}

# Install python3-tk only on appropriate platforms
install_python_tk() {
	if [[ "$OS_NAME" == "Darwin" ]]; then
		if command -v brew >/dev/null 2>&1; then
			echo "Installing python-tk with brew"
			brew install python-tk || echo "brew install python-tk failed"
		else
			echo "Homebrew not found; please install python-tk manually"
		fi
	elif [[ "$OS_NAME" == "Linux" ]]; then
		if [[ "${ID:-}" == "ubuntu" || "${ID_LIKE:-}" == *"ubuntu"* ]]; then
			echo "Installing python3-tk via apt"
			sudo apt-get update || true
			sudo apt-get install -y python3-tk || echo "apt install python3-tk failed"
		elif [[ "${ID:-}" == "fedora" || "${ID_LIKE:-}" == *"fedora"* ]]; then
			echo "Installing python3-tkinter via dnf"
			sudo dnf install -y python3-tkinter || echo "dnf install python3-tkinter failed"
		else
			echo "Skipping python3-tk install on this distro (${ID:-unknown})"
		fi
	else
		echo "Skipping python3-tk install on ${OS_NAME}"
	fi
}

# Try to build/install from source first, fallback to apt if available.
# args: URL DIR_PREFIX APT_PKG
build_or_apt_install() {
	local url="$1"
	local dirname_prefix="$2"
	local apt_pkg="$3"

	local DOWNLOAD_DIR="${HOME}/Downloads"
	mkdir -p "$DOWNLOAD_DIR"
	pushd "$DOWNLOAD_DIR" >/dev/null || return 1

	local tarfile="${dirname_prefix}.tar.gz"
	echo "Downloading $url to $tarfile"
	if command -v curl >/dev/null 2>&1; then
		curl -L -o "$tarfile" "$url" || true
	else
		wget -O "$tarfile" "$url" || true
	fi

	if [[ -f "$tarfile" ]]; then
		echo "Extracting $tarfile"
		tar xf "$tarfile" || true
		# try to find extracted directory
		local dir
		dir=$(tar -tf "$tarfile" | head -n1 | cut -f1 -d"/")
		if [[ -n "$dir" && -d "$dir" ]]; then
			pushd "$dir" >/dev/null || { popd >/dev/null; return 1; }
			echo "Building from source in $(pwd)"
			if ./configure --prefix=/usr/local && make -j"$(nproc)" && sudo make install; then
				sudo ldconfig || true
				popd >/dev/null
				popd >/dev/null
				return 0
			else
				echo "Source build/install failed for $dirname_prefix"
				popd >/dev/null
			fi
		else
			echo "Could not determine extracted directory for $tarfile"
		fi
	else
		echo "Download failed for $url"
	fi

	# fallback to apt if available
	if command -v apt-get >/dev/null 2>&1; then
		echo "Falling back to apt to install $apt_pkg"
		sudo apt-get update || true
		if sudo apt-get install -y "$apt_pkg"; then
			popd >/dev/null
			return 0
		else
			echo "apt install failed for $apt_pkg"
		fi
	else
		echo "apt-get not available; cannot fallback for $apt_pkg"
	fi

	popd >/dev/null
	return 1
}

echo "Starting setup: libgphoto2 + gphoto2 + environment"

# Install python3-tk where appropriate
install_python_tk

# If we have apt available, install common build dependencies so the
# source build of `libgphoto2` is more likely to succeed (e.g. libpopt-dev).
install_build_deps

if [[ "$GPHOTO_PRESENT" -ne 1 ]]; then
	echo "Installing libgphoto2..."
	build_or_apt_install "https://sourceforge.net/projects/gphoto/files/libgphoto/2.5.33/libgphoto2-2.5.33.tar.gz/download" "libgphoto2-2.5.33" "libgphoto2-6" || echo "libgphoto2 installation failed or fallback required"

	echo "Installing gphoto2..."
	build_or_apt_install "https://sourceforge.net/projects/gphoto/files/gphoto/2.5.32/gphoto2-2.5.32.tar.gz/download" "gphoto2-2.5.32" "gphoto2" || echo "gphoto2 installation failed or fallback required"
else
	echo "Skipping libgphoto2/gphoto2 build because gphoto2 is already present."
fi

# create venv and install requirements
if [[ ! -d "./myvenv" ]]; then
	python3 -m venv myvenv || echo "Failed to create venv"
fi
# Activate the virtual environment if present. We only run `pip` commands
# when the venv is actually active to avoid installing packages into the
# system Python accidentally.
if [[ -f "./myvenv/bin/activate" ]]; then
	# shellcheck source=/dev/null
	source ./myvenv/bin/activate || echo "Failed to activate venv"
else
	echo "Virtualenv not found at ./myvenv/bin/activate (it may have failed to create)."
fi

if [[ -n "${VIRTUAL_ENV:-}" ]]; then
	echo "Virtualenv active at: $VIRTUAL_ENV"
	pip install --upgrade pip || true
	pip install -r requirements.txt || echo "pip install of requirements failed"
else
	echo "Virtual environment is not active; skipping pip installs."
	echo "To install requirements, activate the venv and run: source ./myvenv/bin/activate && pip install -r requirements.txt"
fi

# udev rules for odrive
sudo bash -c "curl -fsSL https://cdn.odriverobotics.com/files/odrive-udev-rules.rules > /etc/udev/rules.d/91-odrive.rules && udevadm control --reload-rules && udevadm trigger" || echo "udev rule install failed"

echo "Setup finished. If gphoto2 is still not available, please check the logs above."