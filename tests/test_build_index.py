from __future__ import annotations

from build_index import family_for


def test_wireshark_is_grouped_with_general_security_tools() -> None:
    assert family_for("wireshark-analysis") == "Tools, scanning, and supply chain"
