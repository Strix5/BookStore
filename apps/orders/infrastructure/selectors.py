from apps.orders.infrastructure.models import Order


def get_user_orders(*, user_id: int):
    return (
        Order.objects.filter(user_id=user_id)
        .select_related("user")
        .prefetch_related("items__book")
    )


def get_user_order_detail(*, order_id: int, user_id: int):
    return (
        Order.objects.filter(pk=order_id, user_id=user_id)
        .select_related("user")
        .prefetch_related("items__book")
        .first()
    )
