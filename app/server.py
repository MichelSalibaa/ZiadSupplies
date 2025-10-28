from __future__ import annotations

import json
import logging
import mimetypes
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.parse import urlparse

from .database import create_order, get_catalog, get_order_summary, init_db, seed_data
from .email_service import send_order_confirmation_email

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ziadsupplies.server")

ROOT_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = ROOT_DIR / "templates"
STATIC_DIR = ROOT_DIR / "static"


class RequestHandler(BaseHTTPRequestHandler):
    server_version = "ZiadSupplies/1.0"

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        route = parsed.path

        if route == "/":
            self._serve_template("index.html")
        elif route == "/api/catalog":
            self._serve_catalog()
        elif route.startswith("/static/"):
            self._serve_static(route[len("/static/") :])
        else:
            self.send_error(HTTPStatus.NOT_FOUND, "Page not found")

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        route = parsed.path

        if route == "/api/orders":
            self._handle_create_order()
        else:
            self.send_error(HTTPStatus.NOT_FOUND, "Endpoint not found")

    # ----- Route handlers -------------------------------------------------

    def _serve_template(
        self, template_name: str, context: Optional[Dict[str, str]] = None
    ) -> None:
        template_path = TEMPLATE_DIR / template_name
        if not template_path.exists():
            self.send_error(HTTPStatus.NOT_FOUND, "Template not found")
            return

        content = template_path.read_text(encoding="utf-8")
        if context:
            content = content.format(**context)

        self._send_response(HTTPStatus.OK, "text/html; charset=utf-8", content.encode("utf-8"))

    def _serve_static(self, relative_path: str) -> None:
        try:
            static_root = STATIC_DIR.resolve()
            requested_path = (STATIC_DIR / relative_path).resolve()
        except FileNotFoundError:
            self.send_error(HTTPStatus.NOT_FOUND, "Static asset not found")
            return

        if not str(requested_path).startswith(str(static_root)) or not requested_path.is_file():
            self.send_error(HTTPStatus.NOT_FOUND, "Static asset not found")
            return

        mime_type, _ = mimetypes.guess_type(requested_path.name)
        data = requested_path.read_bytes()
        self._send_response(HTTPStatus.OK, mime_type or "application/octet-stream", data)

    def _serve_catalog(self) -> None:
        try:
            catalog = get_catalog()
            payload = json.dumps({"categories": catalog}).encode("utf-8")
            self._send_response(HTTPStatus.OK, "application/json", payload)
        except Exception as exc:  # pragma: no cover - defensive programming
            logger.exception("Failed to load catalog: {0}".format(exc))
            self._send_error_json(HTTPStatus.INTERNAL_SERVER_ERROR, "Failed to load catalog.")

    def _handle_create_order(self) -> None:
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._send_error_json(HTTPStatus.BAD_REQUEST, "Invalid content length.")
            return

        payload = self.rfile.read(content_length) if content_length > 0 else b""
        try:
            data = json.loads(payload.decode("utf-8")) if payload else {}
        except json.JSONDecodeError:
            self._send_error_json(HTTPStatus.BAD_REQUEST, "Request body must be valid JSON.")
            return

        validation_error = self._validate_order_payload(data)
        if validation_error:
            self._send_error_json(HTTPStatus.BAD_REQUEST, validation_error)
            return

        try:
            order_id = create_order(
                customer_name=data["customerName"].strip(),
                email=data["email"].strip(),
                phone=data["phone"].strip(),
                address=data["address"].strip(),
                items=data["items"],
            )
            summary = get_order_summary(order_id)
            if summary:
                send_order_confirmation_email(summary)

            response = {
                "orderId": order_id,
                "status": "received",
                "message": (
                    "Your order has been received! We'll confirm delivery details shortly via email."
                ),
            }
            self._send_response(
                HTTPStatus.CREATED,
                "application/json",
                json.dumps(response).encode("utf-8"),
            )
        except ValueError as err:
            self._send_error_json(HTTPStatus.BAD_REQUEST, str(err))
        except Exception as exc:  # pragma: no cover - defensive programming
            logger.exception("Failed to create order: %s", exc)
            self._send_error_json(
                HTTPStatus.INTERNAL_SERVER_ERROR,
                "We could not complete your order. Please try again.",
            )

    # ----- Helpers --------------------------------------------------------

    def _send_response(self, status: HTTPStatus, content_type: str, payload: bytes) -> None:
        self.send_response(status.value)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def _send_error_json(self, status: HTTPStatus, message: str) -> None:
        body = json.dumps({"error": message}).encode("utf-8")
        self._send_response(status, "application/json", body)

    def _validate_order_payload(self, data: Dict[str, Any]) -> Optional[str]:
        required_fields = ["customerName", "email", "phone", "address", "items"]
        for field in required_fields:
            if field not in data:
                return f"Missing required field: {field}"

        if not isinstance(data["items"], list) or not data["items"]:
            return "Cart cannot be empty."

        email = str(data["email"]).strip()
        if "@" not in email:
            return "A valid email address is required."

        phone = str(data["phone"]).strip()
        if len(phone) < 6:
            return "Phone number looks too short."

        for item in data["items"]:
            if not isinstance(item, dict):
                return "Each cart item must be an object."
            if "productId" not in item or "quantity" not in item:
                return "Cart items require productId and quantity."

        return None

    def log_message(self, format: str, *args) -> None:  # pragma: no cover - reduce console noise
        logger.info("%s - %s", self.address_string(), format % args)


def run(host: str = "0.0.0.0", port: int = 8000) -> None:
    init_db()
    seed_data()

    server_address = (host, port)
    httpd = ThreadingHTTPServer(server_address, RequestHandler)
    logger.info("Ziad's Supplies server running on http://%s:%s", host, port)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:  # pragma: no cover - CLI convenience
        logger.info("Server interrupted by user, shutting down.")
    finally:
        httpd.server_close()


if __name__ == "__main__":
    run()
