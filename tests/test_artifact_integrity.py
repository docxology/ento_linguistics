"""Real on-disk artifact controls for the standalone validation gate."""
import hashlib
import json

import matplotlib.pyplot as plt
import pytest

from core.provenance import validate_generated_artifacts


def _artifacts(root):
    data = root / "output/data"
    figures = root / "output/figures"
    data.mkdir(parents=True)
    figures.mkdir(parents=True)
    (data / "analysis.json").write_text('{"measured": 1}')
    fig, ax = plt.subplots()
    ax.plot([0, 1, 2], [1, 3, 2])
    path = figures / "observations.png"
    fig.savefig(path)
    plt.close(fig)
    registry = {"fig:observations": {"filename": path.name,
                "metadata": {"sha256": hashlib.sha256(path.read_bytes()).hexdigest()}}}
    (figures / "figure_registry.json").write_text(json.dumps(registry))
    return data, figures


def test_standalone_validation_checks_real_files(tmp_path):
    data, figures = _artifacts(tmp_path)
    validate_generated_artifacts(tmp_path)
    (figures / "observations.png").write_bytes(b"corruption-control")
    with pytest.raises(ValueError, match="hash mismatch"):
        validate_generated_artifacts(tmp_path)
    digest = hashlib.sha256(b"corruption-control").hexdigest()
    (figures / "figure_registry.json").write_text(json.dumps({"fig:a": {"filename": "observations.png", "metadata": {"sha256": digest}}}))
    with pytest.raises(OSError):
        validate_generated_artifacts(tmp_path)


@pytest.mark.parametrize("payload", ['{"value": NaN}', '{}', '[]'])
def test_nonfinite_or_empty_analysis_is_rejected(tmp_path, payload):
    data, _ = _artifacts(tmp_path)
    (data / "analysis.json").write_text(payload)
    with pytest.raises(ValueError):
        validate_generated_artifacts(tmp_path)


def test_extra_image_and_empty_registry_are_rejected(tmp_path):
    _, figures = _artifacts(tmp_path)
    (figures / "unregistered.png").write_bytes((figures / "observations.png").read_bytes())
    with pytest.raises(ValueError, match="inventory"):
        validate_generated_artifacts(tmp_path)
    (figures / "figure_registry.json").write_text('{}')
    with pytest.raises(ValueError, match="registry"):
        validate_generated_artifacts(tmp_path)


def test_registry_cannot_reference_an_external_file(tmp_path):
    _, figures = _artifacts(tmp_path)
    (figures / "figure_registry.json").write_text('{"fig:bad": {"filename": "../outside.png"}}')
    with pytest.raises(ValueError, match="filename"):
        validate_generated_artifacts(tmp_path)


def test_no_artifacts_is_not_a_success(tmp_path):
    with pytest.raises(ValueError, match="No generated"):
        validate_generated_artifacts(tmp_path)


def test_valid_png_checksums_do_not_hide_a_broken_pixel_stream(tmp_path):
    import struct
    import zlib
    from PIL import Image
    _, figures = _artifacts(tmp_path)
    image_path = figures / 'observations.png'
    original = image_path.read_bytes()
    payload = bytearray(original[:8])
    offset = 8
    while offset < len(original):
        size = struct.unpack('>I', original[offset:offset+4])[0]
        kind = original[offset+4:offset+8]
        data = original[offset+8:offset+8+size]
        if kind == b'IDAT':
            data = bytes(size)
        payload.extend(struct.pack('>I', len(data)) + kind + data)
        payload.extend(struct.pack('>I', zlib.crc32(kind+data) & 0xffffffff))
        offset += size+12
    image_path.write_bytes(payload)
    registry_path = figures / 'figure_registry.json'
    registry = json.loads(registry_path.read_text())
    next(iter(registry.values()))['metadata']['sha256'] = hashlib.sha256(payload).hexdigest()
    registry_path.write_text(json.dumps(registry))
    with Image.open(image_path) as image:
        image.verify()
    with Image.open(image_path) as image:
        with pytest.raises(OSError):
            image.load()
    with pytest.raises(OSError):
        validate_generated_artifacts(tmp_path)
