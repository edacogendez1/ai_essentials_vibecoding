"""Price sources. A provider exposes get_cheapest(watch) -> float | None."""
import json
import os
import random
import urllib.parse
import urllib.request


class MockProvider:
    """Random-walk prices, for trying the app without API keys."""

    def __init__(self, seed=None):
        self.rng = random.Random(seed)
        self.base = {}

    def get_cheapest(self, watch):
        base = self.base.setdefault(watch["id"], self.rng.uniform(200, 900))
        return round(base * self.rng.uniform(0.7, 1.3), 2)


class AmadeusProvider:
    """Amadeus Self-Service Flight Offers Search (free tier: developers.amadeus.com).

    Needs AMADEUS_CLIENT_ID and AMADEUS_CLIENT_SECRET. Set AMADEUS_ENV=production
    for live fares; the default test environment returns cached sample data.
    """

    def __init__(self):
        env = os.environ.get("AMADEUS_ENV", "test")
        self.host = "https://api.amadeus.com" if env == "production" else "https://test.api.amadeus.com"
        self.client_id = os.environ["AMADEUS_CLIENT_ID"]
        self.client_secret = os.environ["AMADEUS_CLIENT_SECRET"]
        self._token = None

    def _request(self, req):
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.load(resp)

    def _auth(self):
        if not self._token:
            body = urllib.parse.urlencode({
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            }).encode()
            self._token = self._request(
                urllib.request.Request(f"{self.host}/v1/security/oauth2/token", data=body)
            )["access_token"]
        return self._token

    def get_cheapest(self, watch):
        params = {
            "originLocationCode": watch["origin"],
            "destinationLocationCode": watch["destination"],
            "departureDate": watch["depart_date"],
            "adults": 1,
            "currencyCode": watch["currency"],
            "max": 20,
        }
        if watch["return_date"]:
            params["returnDate"] = watch["return_date"]
        url = f"{self.host}/v2/shopping/flight-offers?{urllib.parse.urlencode(params)}"
        data = self._request(
            urllib.request.Request(url, headers={"Authorization": f"Bearer {self._auth()}"})
        )
        prices = [float(o["price"]["grandTotal"]) for o in data.get("data", [])]
        return min(prices) if prices else None


def get_provider(name):
    if name == "mock":
        return MockProvider()
    if name == "amadeus":
        return AmadeusProvider()
    raise ValueError(f"unknown provider: {name}")
