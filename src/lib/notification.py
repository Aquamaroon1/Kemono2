import copy
import dateutil
import ujson

from typing import Dict, List, Optional

from src.internals.cache.redis import get_conn
from src.internals.database.database import get_cursor

from src.types.account import Notification

def count_account_notifications(account_id: int) -> int:
    args_dict = {
        "account_id": account_id
    }

    cursor = get_cursor()
    query = """
        SELECT
            COUNT(*) AS notifications_count
        FROM notification
        WHERE account_id = %(account_id)s
    """
    cursor.execute(query, args_dict)
    result = cursor.fetchone()
    notifications_count = result["notifications_count"]
    return notifications_count

def get_account_notifications(account_id: int, reload: bool = False) -> List[Notification]:
    redis = get_conn()
    key = f"notifications_for_account:{account_id}"
    notifications = redis.get(key)

    if notifications is None or reload:
        args_dict = {
            "account_id": account_id
        }

        cursor = get_cursor()
        query = """
            SELECT id, account_id, type, created_at, extra_info
            FROM notification
            WHERE account_id = %(account_id)s
            ORDER BY
                created_at DESC
        """
        cursor.execute(query, args_dict)
        result = cursor.fetchall()

        notifications = [Notification.init_from_dict(notification) for notification in result]
        redis.set(key, serialize_notifications(result), ex = 60)

    else:
        notifications = deserialize_notifications(notifications)

    return notifications

def send_notifications(
    account_ids: List[str],
    notification_type: int,
    extra_info: Optional[Dict[str,str]]
) -> bool:
    cursor = get_cursor()

    if not account_ids:
        return False

    if extra_info is not None:
        extra_info = ujson.dumps(extra_info)
        notification_values = f"(%s, {notification_type}, '{extra_info}')"
    else:
        notification_values = f"(%s, {notification_type}, NULL)"

    insert_queries_values_template = ",".join([notification_values] * len(account_ids))
    insert_query = f"""
        INSERT INTO notification (account_id, type, extra_info)
        VALUES {insert_queries_values_template}
        ;
        """
    cursor.execute(insert_query, account_ids)

    return True

def serialize_notification(notification):
    if notification is not None:
        notification = prepare_notification_fields(copy.deepcopy(notification))
    return ujson.dumps(notification)

def deserialize_notification(notification_str):
    notification = ujson.loads(notification_str)
    if notification is not None:
        notification = rebuild_notification_fields(notification)
    return notification

def serialize_notifications(notifications):
    notifications = copy.deepcopy(notifications)
    return ujson.dumps(list(map(lambda notification: prepare_notification_fields(notification), notifications)))

def deserialize_notifications(notifications_str):
    notifications = ujson.loads(notifications_str)
    return list(map(lambda notification: rebuild_notification_fields(notification), notifications))

def prepare_notification_fields(notification):
    notification['created_at'] = notification['created_at'].isoformat()
    return notification

def rebuild_notification_fields(notification):
    notification['created_at'] = dateutil.parser.parse(notification['created_at'])
    return notification
