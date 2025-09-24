from mypy_boto3_s3.type_defs import CompletedPartTypeDef
from pytest_mock import MockerFixture

from msm.apiserver.service import S3Service


class TestS3Service:
    def test_s3_properties(self, s3_service: S3Service) -> None:
        assert s3_service.s3_endpoint == "http://test-endpoint.com"
        assert s3_service.s3_bucket == "test-bucket"
        assert s3_service.s3_path == "test/path"
        assert s3_service.s3_access_key == "test-access-key"
        assert s3_service.s3_secret_key == "test-secret-key"

    def test_s3_client_creation(self, s3_service: S3Service) -> None:
        # Test that s3_client is created and cached
        client1 = s3_service.s3_client
        client2 = s3_service.s3_client
        assert client1 is client2  # Should be the same instance due to caching

    def test_create_multipart_upload(
        self, s3_service: S3Service, mocker: MockerFixture
    ) -> None:
        mock_client = mocker.patch.object(s3_service, "s3_client")
        mock_client.create_multipart_upload.return_value = {
            "UploadId": "test-upload-id"
        }

        s3_key, upload_id = s3_service.create_multipart_upload("test/file.txt")

        assert s3_key == "test/path/test/file.txt"
        assert upload_id == "test-upload-id"
        mock_client.create_multipart_upload.assert_called_once_with(
            ACL="public-read",
            Bucket="test-bucket",
            Key="test/path/test/file.txt",
            ChecksumAlgorithm="SHA256",
        )

    def test_upload_part(
        self, s3_service: S3Service, mocker: MockerFixture
    ) -> None:
        mock_client = mocker.patch.object(s3_service, "s3_client")
        mock_client.upload_part.return_value = {"ETag": "test-etag"}

        etag = s3_service.upload_part(
            "test-key", "test-upload-id", 1, b"test-chunk"
        )

        assert etag == "test-etag"
        mock_client.upload_part.assert_called_once_with(
            Bucket="test-bucket",
            Key="test-key",
            UploadId="test-upload-id",
            PartNumber=1,
            Body=b"test-chunk",
            ChecksumAlgorithm="SHA256",
        )

    def test_complete_upload(
        self, s3_service: S3Service, mocker: MockerFixture
    ) -> None:
        mock_client = mocker.patch.object(s3_service, "s3_client")
        parts = [CompletedPartTypeDef({"ETag": "etag1", "PartNumber": 1})]

        s3_service.complete_upload("test-key", "test-upload-id", parts)

        mock_client.complete_multipart_upload.assert_called_once_with(
            Bucket="test-bucket",
            Key="test-key",
            UploadId="test-upload-id",
            MultipartUpload={"Parts": parts},
        )

    def test_abort_upload(
        self, s3_service: S3Service, mocker: MockerFixture
    ) -> None:
        mock_client = mocker.patch.object(s3_service, "s3_client")

        s3_service.abort_upload("test-key", "test-upload-id")

        mock_client.abort_multipart_upload.assert_called_once_with(
            Bucket="test-bucket",
            Key="test-key",
            UploadId="test-upload-id",
        )

    def test_delete_object(
        self, s3_service: S3Service, mocker: MockerFixture
    ) -> None:
        mock_client = mocker.patch.object(s3_service, "s3_client")

        s3_service.delete_object("test/file.txt")

        mock_client.delete_object.assert_called_once_with(
            Bucket="test-bucket", Key="test/path/test/file.txt"
        )

    def test_get_object(
        self, s3_service: S3Service, mocker: MockerFixture
    ) -> None:
        mock_client = mocker.patch.object(s3_service, "s3_client")
        expected_response = {"Body": b"test-content"}
        mock_client.get_object.return_value = expected_response

        response = s3_service.get_object("test/file.txt")

        assert response["Body"] is not None
        mock_client.get_object.assert_called_once_with(
            Bucket="test-bucket", Key="test/path/test/file.txt"
        )
