from pydantic_core import ValidationError
import pytest

from msm.settings import (
    Settings,
)


class TestSettings:
    def test_from_environ(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("MSM_DB_USER", "myuser")
        monkeypatch.setenv("MSM_DB_NAME", "mydb")
        settings = Settings()
        assert settings.db_user == "myuser"
        assert settings.db_name == "mydb"

    @pytest.mark.parametrize(
        "async_engine,engine",
        [(True, "postgresql+asyncpg"), (False, "postgresql+psycopg")],
    )
    def test_db_dsn(
        self, monkeypatch: pytest.MonkeyPatch, async_engine: bool, engine: str
    ) -> None:
        monkeypatch.setenv("MSM_DB_USER", "myuser")
        monkeypatch.setenv("MSM_DB_NAME", "mydb")
        settings = Settings()
        assert (
            str(settings.db_dsn(async_engine=async_engine))
            == f"{engine}://myuser@localhost:5432/mydb"
        )

    def test_heartbeat_setting(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("MSM_HEARTBEAT_INTERVAL_SEC", "200")
        settings = Settings()
        assert settings.heartbeat_interval_seconds == 200

    def test_conn_lost_threshold_setting(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("MSM_CONN_LOST_THRESHOLD_SEC", "400")
        settings = Settings()
        assert settings.conn_lost_threshold_seconds == 400

    def test_conn_lost_thresh_validator(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("MSM_HEARTBEAT_INTERVAL_SEC", "200")
        monkeypatch.setenv("MSM_CONN_LOST_THRESHOLD_SEC", "100")
        with pytest.raises(
            ValidationError,
            match=r"threshold \(100s\) should be greater than heartbeat",
        ):
            settings = Settings()

    def test_s3_settings(self, monkeypatch: pytest.MonkeyPatch) -> None:
        s3_settings = {
            "MSM_S3_ACCESS_KEY": "test-access-key",
            "MSM_S3_SECRET_KEY": "test-secret-key",
            "MSM_S3_ENDPOINT": "test-endpoint",
            "MSM_S3_BUCKET": "test-bucket",
            "MSM_S3_PATH": "test-path",
        }
        for k in s3_settings:
            monkeypatch.setenv(k, s3_settings[k])
        settings = Settings()
        assert settings.s3_access_key == s3_settings["MSM_S3_ACCESS_KEY"]
        assert settings.s3_secret_key == s3_settings["MSM_S3_SECRET_KEY"]
        assert settings.s3_endpoint == s3_settings["MSM_S3_ENDPOINT"]
        assert settings.s3_bucket == s3_settings["MSM_S3_BUCKET"]
        assert settings.s3_path == s3_settings["MSM_S3_PATH"]
