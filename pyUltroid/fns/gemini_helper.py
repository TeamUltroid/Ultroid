# Ultroid - UserBot
# Copyright (C) 2021-2024 TeamUltroid
#
# This file is a part of < https://github.com/TeamUltroid/Ultroid/ >
# PLease read the GNU Affero General Public License in
# <https://github.com/TeamUltroid/pyUltroid/blob/main/LICENSE>.

import asyncio
import requests
from pymongo import MongoClient


class GeminiUltroid:
    def init(
        self,
        api_key: str = None,
        mongo_url: str = None,
        api_base="https://generativelanguage.googleapis.com",
        version: str = "v1beta",
        model: str = "models/gemini-pro",
        content: str = "generateContent",
        user_id: int = None,
        oracle_base: str = "You are an AI called Ultroid AI",
    ):
        self.api_key = api_key
        self.api_base = api_base
        self.version = version
        self.model = model
        self.content = content
        self.user_id = user_id
        self.oracle_base = oracle_base
        self.mongo_url = mongo_url
        self.client = MongoClient(self.mongo_url)
        self.db = self.client.tiktokbot
        self.collection = self.db.users

    def _close(self):
        self.client.close()

    async def __get_resp_gu(self, query: str = None):
        try:
            gemini_chat = await self._get_gu_chat_from_db()
            gemini_chat.append({"role": "user", "parts": [{"text": query}]})
            api_method = f"{self.api_base}/{self.version}/{self.model}:{self.content}?key={self.api_key}"
            headers = {"Content-Type": "application/json"}
            payload = {"contents": gemini_chat}
            response = await asyncio.to_thread(
                requests.post, api_method, headers=headers, json=payload
            )

            if response.status_code != 200:
                return "Error responding", gemini_chat

            response_data = response.json()
            answer = (
                response_data.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [{}])[0]
                .get("text", "")
            )

            gemini_chat.append({"role": "model", "parts": [{"text": answer}]})
            await self._updts_gu_chat_in_db(gemini_chat)
            return answer, gemini_chat
        except Exception as e:
            error_msg = f"Error response: {e}"
            return error_msg, gemini_chat

    async def _get_gu_chat_from_db(self):
        get_data_user = {"user_id": self.user_id}
        document = self.collection.find_one(get_data_user)
        return document.get("gemini_chat", []) if document else []

    async def _updts_gu_chat_in_db(self, gemini_chat):
        get_data_user = {"user_id": self.user_id}
        document = self.collection.find_one(get_data_user)
        if document:
            self.collection.update_one(
                {"_id": document["_id"]}, {"$set": {"gemini_chat": gemini_chat}}
            )
        else:
            self.collection.insert_one(
                {"user_id": self.user_id, "gemini_chat": gemini_chat}
            )

    async def _clear_history_in_db(self):
        unset_clear = {"gemini_chat": None}
        return self.collection.update_one(
            {"user_id": self.user_id}, {"$unset": unset_clear}
        )
