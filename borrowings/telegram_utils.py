import requests

from library_api.settings import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID


def send_telegram_notification(
        borrowing_id,
        borrow_date,
        expected_return_date,
        book,
        user,
):

    message = (
        f"New borrowing № {borrowing_id} was created \n"
        f"Borrowing date: {borrow_date}\n"
        f"Return by: {expected_return_date}\n"
        f"Book: {book}\n"
        f"User: {user}"

    )

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
    }

    requests.post(url, json=payload)
