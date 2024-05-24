from io import BytesIO

from flask import Blueprint, send_from_directory, url_for
import os
import config

minio = None


def init_obj_store(app):
    if config.MINIO_URL is not None:
        from flask_minio import Minio
        global minio
        minio = Minio()
        minio.init_app(app)
        app.logger.info("Using MinIO object store.")
    else:
        app.logger.warn("Using local object store! For production and best performance configure an S3 compatible store!")
        objs = Blueprint("objs", __name__, url_prefix="/objs")

        os.makedirs("store", exist_ok=True)

        @objs.route("/<bucket>/<name>")
        def get_obj(bucket, name):
            with open(os.path.join("store", bucket, name) + "_meta", "r") as f:
                content_type = f.read()
            return send_from_directory(os.path.join("store", bucket), name, mimetype=content_type)

        app.register_blueprint(objs)


def put_object(bucket_name: str, object_name: str, object_content: BytesIO, content_length: int, content_type: str):
    if minio is not None:
        minio.client.put_object(bucket_name, object_name, object_content, content_length,
                                content_type=content_type)
    else:
        import os
        path = os.path.join("store", bucket_name)
        os.makedirs(path, exist_ok=True)
        with open(os.path.join(path, object_name), "wb") as f:
            f.write(object_content.getbuffer())
        with open(os.path.join(path, object_name) + "_meta", "w") as f:
            f.write(content_type)


def get_object_url(bucket_name: str, object_name: str) -> str:
    if minio is not None:
        return "//" + config.MINIO_URL + "/" + bucket_name + "/" + object_name
    else:
        return url_for("objs.get_obj", bucket=bucket_name, name=object_name)
