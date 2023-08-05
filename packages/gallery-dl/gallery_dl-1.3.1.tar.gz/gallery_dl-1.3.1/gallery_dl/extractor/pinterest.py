# -*- coding: utf-8 -*-

# Copyright 2016-2018 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extract images from https://www.pinterest.com"""

from .common import Extractor, Message
from .. import text, util, exception


class PinterestExtractor(Extractor):
    """Base class for pinterest extractors"""
    category = "pinterest"
    filename_fmt = "{category}_{pin_id}.{extension}"
    archive_fmt = "{pin_id}"

    def __init__(self):
        Extractor.__init__(self)
        self.api = PinterestAPI(self)

    def data_from_pin(self, pin):
        """Get image url and metadata from a pin-object"""
        img = pin["image"]["original"]
        url = img["url"]
        data = {
            "pin_id": util.safe_int(pin["id"]),
            "note": pin["note"],
            "width": util.safe_int(img["width"]),
            "height": util.safe_int(img["height"]),
        }
        return url, text.nameext_from_url(url, data)


class PinterestPinExtractor(PinterestExtractor):
    """Extractor for images from a single pin from pinterest.com"""
    subcategory = "pin"
    pattern = [r"(?:https?://)?(?:[^./]+\.)?pinterest\.[^/]+/pin/([^/?#&]+)"]
    test = [
        ("https://www.pinterest.com/pin/858146903966145189/", {
            "url": "afb3c26719e3a530bb0e871c480882a801a4e8a5",
            "keyword": "f651cb271247f306d1d30385d49c7b82da44c2b1",
            "content": "d3e24bc9f7af585e8c23b9136956bd45a4d9b947",
        }),
        ("https://www.pinterest.com/pin/858146903966145188/", {
            "exception": exception.NotFoundError,
        }),
    ]

    def __init__(self, match):
        PinterestExtractor.__init__(self)
        self.pin_id = match.group(1)

    def items(self):
        pin = self.api.pin(self.pin_id)
        url, data = self.data_from_pin(pin)
        yield Message.Version, 1
        yield Message.Directory, data
        yield Message.Url, url, data


class PinterestBoardExtractor(PinterestExtractor):
    """Extractor for images from a board from pinterest.com"""
    subcategory = "board"
    directory_fmt = ["{category}", "{user}", "{board}"]
    pattern = [r"(?:https?://)?(?:[^./]+\.)?pinterest\.[^/]+/"
               r"(?!pin/)([^/?#&]+)/([^/?#&]+)"]
    test = [
        ("https://www.pinterest.com/g1952849/test-/", {
            "url": "85911dfca313f3f7f48c2aa0bc684f539d1d80a6",
            "keyword": "c54cf5aa830994f2ed4871efa7154a5fdaa1c2ce",
        }),
        ("https://www.pinterest.com/g1952848/test/", {
            "exception": exception.NotFoundError,
        }),
    ]

    def __init__(self, match):
        PinterestExtractor.__init__(self)
        self.user, self.board = match.groups()

    def items(self):
        board = self.api.board(self.user, self.board)
        data = self.data_from_board(board)
        num = data["count"]
        yield Message.Version, 1
        yield Message.Directory, data
        for pin in self.api.board_pins(self.user, self.board):
            url, pdata = self.data_from_pin(pin)
            data.update(pdata)
            data["num"] = num
            num -= 1
            yield Message.Url, url, data

    def data_from_board(self, board):
        """Get metadata from a board-object"""
        data = {
            "user": self.user,
            "board_id": util.safe_int(board["id"]),
            "board": board["name"],
            "count": board["counts"]["pins"],
        }
        return data


class PinterestPinitExtractor(PinterestExtractor):
    """Extractor for images from a pin.it URL"""
    subcategory = "pinit"
    pattern = [r"(?:https?://)?(pin\.it/[^/?#&]+)"]
    test = [
        ("https://pin.it/Hvt8hgT", {
            "url": "8daad8558382c68f0868bdbd17d05205184632fa",
        }),
        ("https://pin.it/Hvt8hgS", {
            "exception": exception.NotFoundError,
        }),
    ]

    def __init__(self, match):
        PinterestExtractor.__init__(self)
        self.url = "https://" + match.group(1)

    def items(self):
        response = self.session.head(self.url)
        location = response.headers.get("Location")
        if not location or location in ("https://api.pinterest.com/None",
                                        "https://www.pinterest.com"):
            raise exception.NotFoundError("pin")
        yield Message.Queue, location, {}


class PinterestAPI():
    """Minimal interface for the pinterest API"""

    def __init__(self, extractor, access_token="AV2U9Oe6dyC2vfPugUnBvJ7Duxg9"
                                               "FHCJPXPZIvRDXv9hvwBALwAAAAA"):
        access_token = extractor.config("access-token", access_token)
        self.session = extractor.session
        self.session.params["access_token"] = access_token

    def pin(self, pin_id, fields="id,image,note"):
        """Query information about a pin"""
        params = {"fields": fields}
        response = self.session.get(
            "https://api.pinterest.com/v1/pins/{pin}/".format(pin=pin_id),
            params=params
        )
        return self._parse(response)["data"]

    def board(self, user, board, fields="id,name,counts"):
        """Query information about a board"""
        params = {"fields": fields}
        response = self.session.get(
            "https://api.pinterest.com/v1/boards/{user}/{board}/"
            .format(user=user, board=board), params=params
        )
        return self._parse(response)["data"]

    def board_pins(self, user, board, fields="id,image,note"):
        """Yield all pins of a specific board"""
        params = {"fields": fields}
        url = ("https://api.pinterest.com/v1/boards/{user}/{board}/pins/"
               .format(user=user, board=board))
        while True:
            response = self._parse(self.session.get(url, params=params))
            yield from response["data"]

            cursor = response["page"]["cursor"]
            if not cursor:
                return
            params["cursor"] = cursor

    @staticmethod
    def _parse(response):
        """Parse an API response"""
        data = response.json()
        if "data" not in data or data["data"] is None:
            try:
                msg = data["message"].partition(" ")[0].lower()
            except KeyError:
                msg = ""
            raise exception.NotFoundError(msg)
        return data
