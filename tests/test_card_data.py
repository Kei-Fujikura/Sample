from poketcg.card_data import PokemonCardClient, RemoteCard


class DummyResponse:
    def __init__(self, text: str):
        self._text = text

    def read(self) -> bytes:
        return self._text.encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        return None


def test_client_extracts_metadata(monkeypatch):
    html = """
    <html>
      <head>
        <meta property="og:title" content="ピカチュウ" />
        <meta property="og:image" content="https://example.com/pika.png" />
      </head>
    </html>
    """

    def fake_urlopen(url, timeout):
        assert url.endswith("/card/123")
        return DummyResponse(html)

    monkeypatch.setattr("poketcg.card_data.urlopen", fake_urlopen)
    client = PokemonCardClient()

    card = client.fetch(123)
    assert isinstance(card, RemoteCard)
    assert card.name == "ピカチュウ"
    assert card.image_url == "https://example.com/pika.png"
    assert card.detail_url.endswith("/card/123")


def test_fetch_range_skips_failures(monkeypatch):
    html_ok = """
    <html><head><meta property="og:title" content="フシギダネ" /><meta property="og:image" content="https://example.com/bulba.png" /></head></html>
    """

    responses = {
        100: DummyResponse(html_ok),
        101: None,
        102: DummyResponse(html_ok),
    }

    def fake_urlopen(url, timeout):
        card_id = int(url.split("/")[-1])
        resp = responses.get(card_id)
        if resp is None:
            raise ValueError("not found")
        return resp

    monkeypatch.setattr("poketcg.card_data.urlopen", fake_urlopen)
    client = PokemonCardClient()

    cards = client.fetch_range(100, 102)
    assert [card.card_id for card in cards] == [100, 102]
