"""Minimal Twilio Connector webhook for LiveKit.

Twilio POSTs here on an incoming call. We ask LiveKit for a connector
WebSocket URL and return it as TwiML, which bridges the call into a room.

Standard library only. Run:
    python twilio_webhook.py
"""

import asyncio
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs

from dotenv import load_dotenv
from livekit import api
from livekit.protocol.agent_dispatch import RoomAgentDispatch

load_dotenv()

AGENT_NAME = "phone-agent"


async def get_twiml(from_number: str, call_sid: str) -> str:
    lkapi = api.LiveKitAPI()
    try:
        res = await lkapi.connector.connect_twilio_call(
            api.ConnectTwilioCallRequest(
                twilio_call_direction=(
                    api.ConnectTwilioCallRequest.TwilioCallDirection.TWILIO_CALL_DIRECTION_INBOUND
                ),
                room_name=f"call-{call_sid}",
                participant_identity=from_number,
                agents=[RoomAgentDispatch(agent_name=AGENT_NAME)],
            )
        )
    finally:
        await lkapi.aclose()

    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        "<Response>"
        f'<Connect><Stream url="{res.connect_url}" /></Connect>'
        "</Response>"
    )


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path != "/health":
            self.send_error(404)
            return

        body = b"ok\n"
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self) -> None:
        body = self.rfile.read(int(self.headers["Content-Length"])).decode()
        form = parse_qs(body)

        twiml = asyncio.run(
            get_twiml(form["From"][0], form["CallSid"][0])
        ).encode()

        self.send_response(200)
        self.send_header("Content-Type", "application/xml")
        self.send_header("Content-Length", str(len(twiml)))
        self.end_headers()
        self.wfile.write(twiml)


if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    print(f"listening on port {port}")
    HTTPServer(("", port), Handler).serve_forever()
