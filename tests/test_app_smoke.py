from pathlib import Path

from streamlit.testing.v1 import AppTest


def test_streamlit_app_loads_without_exception():
    app_path = Path(__file__).resolve().parents[1] / "app.py"
    app = AppTest.from_file(str(app_path), default_timeout=45).run()

    assert not app.exception
