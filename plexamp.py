"""Helpers for preparing Plexamp companion API requests."""

from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


PLAY_MEDIA_PATH = "/player/playback/playMedia"


class InvalidPlaybackURL(ValueError):
    """Raised when an autoplay URL cannot identify its Plex server."""


def prepare_playback_url(url):
    """Add the Plex server identifier required by direct Plexamp requests.

    Plex web links normally derive ``machineIdentifier`` from the authority of
    their nested ``server://`` URI. Direct companion API calls bypass that web
    client preparation, so reproduce it here for playMedia requests.
    """
    parsed_url = urlsplit(url)
    if parsed_url.path != PLAY_MEDIA_PATH:
        return url

    query_items = parse_qsl(parsed_url.query, keep_blank_values=True)
    inner_uri = next(
        (value for key, value in query_items if key == "uri"),
        None,
    )
    if inner_uri is None:
        raise InvalidPlaybackURL("playMedia URL is missing its uri parameter")

    parsed_uri = urlsplit(inner_uri)
    if parsed_uri.scheme != "server" or not parsed_uri.netloc:
        raise InvalidPlaybackURL(
            "playMedia uri must use the server://<machine-id>/... format"
        )

    if any(key == "machineIdentifier" for key, _ in query_items):
        return url

    query_items.append(("machineIdentifier", parsed_uri.netloc))
    return urlunsplit(
        (
            parsed_url.scheme,
            parsed_url.netloc,
            parsed_url.path,
            urlencode(query_items),
            parsed_url.fragment,
        )
    )
