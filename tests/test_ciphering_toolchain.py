import pytest
import random
from os import listdir

from client.ciphering_toolchain import create_observer_thread, apply_entire_encryption_algorithm, \
    apply_entire_decryption_algorithm, get_data_from_video

from wacryptolib.container import (
    LOCAL_ESCROW_PLACEHOLDER,
)

SIMPLE_SHAMIR_CONTAINER_CONF = dict(
    data_encryption_strata=[
        dict(
            data_encryption_algo="AES_CBC",
            key_encryption_strata=[
                dict(
                    key_encryption_algo="RSA_OAEP", key_escrow=LOCAL_ESCROW_PLACEHOLDER
                ),
                dict(
                    key_encryption_algo="SHARED_SECRET",
                    key_shared_secret_threshold=3,
                    key_shared_secret_escrows=[
                        dict(
                            share_encryption_algo="RSA_OAEP",
                            # shared_escrow=dict(url="http://example.com/jsonrpc"),
                            share_escrow=LOCAL_ESCROW_PLACEHOLDER,
                        ),
                        dict(
                            share_encryption_algo="RSA_OAEP",
                            # shared_escrow=dict(url="http://example.com/jsonrpc"),
                            share_escrow=LOCAL_ESCROW_PLACEHOLDER,
                        ),
                        dict(
                            share_encryption_algo="RSA_OAEP",
                            # shared_escrow=dict(url="http://example.com/jsonrpc"),
                            share_escrow=LOCAL_ESCROW_PLACEHOLDER,
                        ),
                        dict(
                            share_encryption_algo="RSA_OAEP",
                            # shared_escrow=dict(url="http://example.com/jsonrpc"),
                            share_escrow=LOCAL_ESCROW_PLACEHOLDER,
                        ),
                        dict(
                            share_encryption_algo="RSA_OAEP",
                            # shared_escrow=dict(url="http://example.com/jsonrpc"),
                            share_escrow=LOCAL_ESCROW_PLACEHOLDER,
                        ),
                    ],
                ),
            ],
            data_signatures=[
                dict(
                    message_prehash_algo="SHA256",
                    signature_algo="DSA_DSS",
                    signature_escrow=LOCAL_ESCROW_PLACEHOLDER,
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
                dict(
                    key_encryption_algo="RSA_OAEP", key_escrow=LOCAL_ESCROW_PLACEHOLDER
                )
            ],
            data_signatures=[],
        ),
        dict(
            data_encryption_algo="AES_CBC",
            key_encryption_strata=[
                dict(
                    key_encryption_algo="RSA_OAEP", key_escrow=LOCAL_ESCROW_PLACEHOLDER
                )
            ],
            data_signatures=[
                dict(
                    message_prehash_algo="SHA3_512",
                    signature_algo="DSA_DSS",
                    signature_escrow=LOCAL_ESCROW_PLACEHOLDER,
                )
            ],
        ),
        dict(
            data_encryption_algo="CHACHA20_POLY1305",
            key_encryption_strata=[
                dict(
                    key_encryption_algo="SHARED_SECRET",
                    key_shared_secret_threshold=2,
                    key_shared_secret_escrows=[
                        dict(
                            share_encryption_algo="RSA_OAEP",
                            # shared_escrow=dict(url="http://example.com/jsonrpc"),
                            share_escrow=LOCAL_ESCROW_PLACEHOLDER,
                        ),
                        dict(
                            share_encryption_algo="RSA_OAEP",
                            # shared_escrow=dict(url="http://example.com/jsonrpc"),
                            share_escrow=LOCAL_ESCROW_PLACEHOLDER,
                        ),
                        dict(
                            share_encryption_algo="RSA_OAEP",
                            # shared_escrow=dict(url="http://example.com/jsonrpc"),
                            share_escrow=LOCAL_ESCROW_PLACEHOLDER,
                        ),
                        dict(
                            share_encryption_algo="RSA_OAEP",
                            # shared_escrow=dict(url="http://example.com/jsonrpc"),
                            share_escrow=LOCAL_ESCROW_PLACEHOLDER,
                        ),
                    ],
                ),
            ],
            data_signatures=[
                dict(
                    message_prehash_algo="SHA3_256",
                    signature_algo="RSA_PSS",
                    signature_escrow=LOCAL_ESCROW_PLACEHOLDER,
                ),
                dict(
                    message_prehash_algo="SHA512",
                    signature_algo="ECC_DSS",
                    signature_escrow=LOCAL_ESCROW_PLACEHOLDER,
                ),
            ],
        ),
    ]
)


@pytest.mark.parametrize(
    "container_conf", [SIMPLE_SHAMIR_CONTAINER_CONF, COMPLEX_SHAMIR_CONTAINER_CONF]
)
def test_encrypt_video_stream(container_conf):
    video_files = listdir("ffmpeg_video_stream")
    path = f"ffmpeg_video_stream/{random.choice(video_files)}"
    encryption_algo = "RSA_OAEP"
    key_length_bits = random.choice([2048, 3072, 4096])
    metadata = random.choice([None, dict(a=[123])])

    encryption_data = apply_entire_encryption_algorithm(
        key_type=encryption_algo, conf=container_conf, path=path, key_length_bits=key_length_bits, metadata=metadata
    )

    assert isinstance(encryption_data, dict)
    assert isinstance(encryption_data["private_key"], dict)
    assert isinstance(encryption_data["encryption_algo"], str)
    assert isinstance(encryption_data["data"], dict)

    result_data = apply_entire_decryption_algorithm(encryption_data=encryption_data)

    assert isinstance(result_data, bytes)
    data = get_data_from_video(path=path)

    assert result_data == data


def test_create_observer_thread():
    create_observer_thread()
