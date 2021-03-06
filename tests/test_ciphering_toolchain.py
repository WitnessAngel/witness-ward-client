import pytest
import random
import os
from pathlib import Path
import time

from client.ciphering_toolchain import (
    RecordingToolchain,
    NewVideoHandler,
    save_container,
    generate_asymmetric_keypair,
)
from wacryptolib.utilities import generate_uuid0

from wacryptolib.container import (
    LOCAL_ESCROW_MARKER,
    SHARED_SECRET_MARKER,
    decrypt_data_from_container,
    load_container_from_filesystem,
)
from wacryptolib.key_storage import FilesystemKeyStorage

SIMPLE_SHAMIR_CONTAINER_CONF = dict(
    data_encryption_strata=[
        dict(
            data_encryption_algo="AES_CBC",
            key_encryption_strata=[
                dict(key_encryption_algo="RSA_OAEP", key_escrow=LOCAL_ESCROW_MARKER),
                dict(
                    key_encryption_algo=SHARED_SECRET_MARKER,
                    key_shared_secret_threshold=3,
                    key_shared_secret_escrows=[
                        dict(
                            share_encryption_algo="RSA_OAEP",
                            # shared_escrow=dict(url="http://example.com/jsonrpc"),
                            share_escrow=LOCAL_ESCROW_MARKER,
                        ),
                        dict(
                            share_encryption_algo="RSA_OAEP",
                            # shared_escrow=dict(url="http://example.com/jsonrpc"),
                            share_escrow=LOCAL_ESCROW_MARKER,
                        ),
                        dict(
                            share_encryption_algo="RSA_OAEP",
                            # shared_escrow=dict(url="http://example.com/jsonrpc"),
                            share_escrow=LOCAL_ESCROW_MARKER,
                        ),
                        dict(
                            share_encryption_algo="RSA_OAEP",
                            # shared_escrow=dict(url="http://example.com/jsonrpc"),
                            share_escrow=LOCAL_ESCROW_MARKER,
                        ),
                        dict(
                            share_encryption_algo="RSA_OAEP",
                            # shared_escrow=dict(url="http://example.com/jsonrpc"),
                            share_escrow=LOCAL_ESCROW_MARKER,
                        ),
                    ],
                ),
            ],
            data_signatures=[
                dict(
                    message_prehash_algo="SHA256",
                    signature_algo="DSA_DSS",
                    signature_escrow=LOCAL_ESCROW_MARKER,
                )
            ],
        )
    ]
)

COMPLEX_SHAMIR_CONTAINER_CONF = dict(
    data_encryption_strata=[
        dict(
            data_encryption_algo="AES_EAX",
            key_encryption_strata=[
                dict(key_encryption_algo="RSA_OAEP", key_escrow=LOCAL_ESCROW_MARKER)
            ],
            data_signatures=[],
        ),
        dict(
            data_encryption_algo="AES_CBC",
            key_encryption_strata=[
                dict(key_encryption_algo="RSA_OAEP", key_escrow=LOCAL_ESCROW_MARKER)
            ],
            data_signatures=[
                dict(
                    message_prehash_algo="SHA3_512",
                    signature_algo="DSA_DSS",
                    signature_escrow=LOCAL_ESCROW_MARKER,
                )
            ],
        ),
        dict(
            data_encryption_algo="CHACHA20_POLY1305",
            key_encryption_strata=[
                dict(
                    key_encryption_algo=SHARED_SECRET_MARKER,
                    key_shared_secret_threshold=2,
                    key_shared_secret_escrows=[
                        dict(
                            share_encryption_algo="RSA_OAEP",
                            # shared_escrow=dict(url="http://example.com/jsonrpc"),
                            share_escrow=LOCAL_ESCROW_MARKER,
                        ),
                        dict(
                            share_encryption_algo="RSA_OAEP",
                            # shared_escrow=dict(url="http://example.com/jsonrpc"),
                            share_escrow=LOCAL_ESCROW_MARKER,
                        ),
                        dict(
                            share_encryption_algo="RSA_OAEP",
                            # shared_escrow=dict(url="http://example.com/jsonrpc"),
                            share_escrow=LOCAL_ESCROW_MARKER,
                        ),
                        dict(
                            share_encryption_algo="RSA_OAEP",
                            # shared_escrow=dict(url="http://example.com/jsonrpc"),
                            share_escrow=LOCAL_ESCROW_MARKER,
                        ),
                    ],
                )
            ],
            data_signatures=[
                dict(
                    message_prehash_algo="SHA3_256",
                    signature_algo="RSA_PSS",
                    signature_escrow=LOCAL_ESCROW_MARKER,
                ),
                dict(
                    message_prehash_algo="SHA512",
                    signature_algo="ECC_DSS",
                    signature_escrow=LOCAL_ESCROW_MARKER,
                ),
            ],
        ),
    ]
)


@pytest.mark.parametrize("container_conf", [SIMPLE_SHAMIR_CONTAINER_CONF])
def test_create_observer_thread(container_conf):
    encryption_algo = "RSA_OAEP"
    new_video_handler = NewVideoHandler(
        conf=container_conf,
        key_type=encryption_algo,
        recordings_folder="ffmpeg_video_stream/",
    )
    new_video_handler.start_observer()


def test_decipher_container():
    video_files = os.listdir("ciphered_video_stream/")
    for file in video_files:
        if file.endswith(".crypt"):
            container = load_container_from_filesystem(
                container_filepath=Path("ciphered_video_stream/{}".format(file))
            )
            decrypt_data_from_container(container=container)


@pytest.mark.parametrize("container_conf", [SIMPLE_SHAMIR_CONTAINER_CONF])
def test_recording_toolchain(container_conf):
    key_type = "RSA_OAEP"
    # camera_url = "rtsp://wowzaec2demo.streamlock.net/vod/mp4:BigBuckBunny_115k.mov"
    camera_url = "rtsp://viewer:SomePwd8162@92.89.81.50:554/Streaming/Channels/101"
    recording_time = 30
    segment_time = 10
    recording_toolchain = RecordingToolchain(
        recordings_folder="ffmpeg_video_stream/",
        conf=container_conf,
        key_type=key_type,
        camera_url=camera_url,
        recording_time=str(recording_time),
        segment_time=str(segment_time),
    )
    recording_toolchain.launch_recording_toolchain()
    time.sleep(recording_time)
    recording_toolchain.stop_recording_toolchain_and_wait()
    assert os.listdir("ffmpeg_video_stream/") == []

    # Assert every segment have been ciphered
    ciphered_segment = 0
    ciphered_videos = os.listdir("ciphered_video_stream/")
    for ciphered_video in ciphered_videos:
        if ciphered_video.endswith(".crypt"):
            ciphered_segment += 1

    assert ciphered_segment >= (recording_time / segment_time)
