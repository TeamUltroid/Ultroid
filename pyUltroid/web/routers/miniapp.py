# Ultroid - UserBot
# Copyright (C) 2021-2025 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/pyUltroid/blob/main/LICENSE>.

import logging
from aiohttp import web
from telethon import events
from telethon.tl.functions.messages import SetBotPrecheckoutResultsRequest
from telethon.tl.functions.payments import ExportInvoiceRequest
from telethon.tl.types import (
    DataJSON,
    InputInvoiceMessage,
    InputMediaInvoice,
    LabeledPrice,
    Invoice,
    UpdateBotPrecheckoutQuery,
)

from ... import asst, udB
from ..decorators import route, setup_routes
from .admin import check_owner, is_owner

logger = logging.getLogger(__name__)


@asst.on(events.Raw(types=UpdateBotPrecheckoutQuery))
async def handle_precheckout_query(event: UpdateBotPrecheckoutQuery):
    """Handle pre-checkout queries to confirm transactions."""
    logger.info(f"Received pre-checkout query: {event}")
    try:
        await asst(
            SetBotPrecheckoutResultsRequest(
                query_id=event.query_id,
                success=True,
            )
        )
        logger.info(f"Successfully answered pre-checkout query: {event.query_id}")
    except Exception as e:
        logger.error(
            f"Failed to answer pre-checkout query {event.query_id}: {e}", exc_info=True
        )
        # Deny the transaction on failure
        await asst(
            SetBotPrecheckoutResultsRequest(
                query_id=event.query_id,
                success=False,
                error="An internal error occurred. Please try again later.",
            )
        )


@route(
    "/api/miniapp/create_invoice",
    method="POST",
    description="Create a donation invoice",
)
async def handle_create_invoice(request: web.Request) -> web.Response:

    try:
        data = await request.json()
        amount = int(data.get("amount"))

        if not amount:
            return web.json_response({"error": "amount is required"}, status=400)

        # For XTR (Stars), no provider token is needed.
        # The provider is Telegram.
        title = f"Donate {amount} Stars"
        description = f"Support Ultroid by donating {amount} Telegram Stars. ✨"
        payload = f"ultroid_stars_{amount}".encode()

        # Create the invoice media
        invoice_media = InputMediaInvoice(
            title=title,
            description=description,
            invoice=Invoice(
                currency="XTR",
                prices=[LabeledPrice(label=f"{amount} Star(s)", amount=amount)],
                test=False,  # Set to False for real transactions
                phone_requested=False,
                email_requested=False,
                shipping_address_requested=False,
                flexible=False,
            ),
            payload=payload,
            provider="telegram",
            provider_data=DataJSON(data="{}"),
            start_param="ultroid-donation",
        )

        # Export the invoice link
        exported_invoice = await asst(
            ExportInvoiceRequest(
                invoice_media=invoice_media
            )
        )

        return web.json_response({"url": exported_invoice.url})

    except Exception as e:
        logger.error(f"Failed to create invoice: {e}", exc_info=True)
        return web.json_response(
            {"error": f"Failed to create invoice: {str(e)}"}, status=500
        )


handlers = [handle_create_invoice]


def setup_miniapp_routes(app: web.Application) -> None:
    """Setup miniapp routes."""
    setup_routes(app, handlers)
