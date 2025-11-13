import minio
import contextlib
from dependency_injector.wiring import Provide, inject

@contextlib.asynccontextmanager
@inject
async def app_lifespan(_,
                       fs_client: minio.Minio = Provide['fs_client'],
                       fs_prof_images_bucket_name: str = Provide['config.fs.profile_images_bucket'],
                       fs_attachments_bucket_name: str = Provide['config.fs.attachments_bucket']):
    # startup
    # create minio buckets if needed
    for bucket in (fs_prof_images_bucket_name, fs_attachments_bucket_name):
        if not fs_client.bucket_exists(bucket):
            fs_client.make_bucket(bucket)

    yield

    # cleanup