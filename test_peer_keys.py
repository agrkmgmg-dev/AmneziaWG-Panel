from backend.app.models.peer import Peer
from backend.app.schemas.peer import PeerResponse
from backend.app.services.key_generator import KeyGeneratorService


def test_peer_keypair_generation():
    generator = KeyGeneratorService()

    private_key, public_key = generator.generate_keypair()

    assert private_key
    assert public_key

    assert private_key != "pending"
    assert public_key != "pending"

    assert len(private_key) == 44
    assert len(public_key) == 44

    assert private_key != public_key


def test_keypair_generation_is_unique():
    generator = KeyGeneratorService()

    private_key_1, public_key_1 = generator.generate_keypair()
    private_key_2, public_key_2 = generator.generate_keypair()

    assert private_key_1 != private_key_2
    assert public_key_1 != public_key_2


def test_peer_response_does_not_expose_private_key():
    fields = PeerResponse.model_fields

    assert "private_key" not in fields
    assert "public_key" in fields
    assert "id" in fields
    assert "user_id" in fields


def test_peer_model_contains_key_fields():
    fields = Peer.__table__.columns

    assert "private_key" in fields
    assert "public_key" in fields

    assert fields["private_key"].nullable is True
    assert fields["public_key"].nullable is False
    assert fields["public_key"].unique is True