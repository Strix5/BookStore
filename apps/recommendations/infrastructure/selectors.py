from django.db.models import Prefetch

from apps.recommendations.infrastructure.models import Recommendation, RecommendationBook


def get_active_recommendations():
    return (
        Recommendation.objects
        .filter(is_active=True)
        .prefetch_related(
            "translations",
            Prefetch(
                "recommendation_books",
                queryset=RecommendationBook.objects.select_related("book").order_by("order")
            )
        )
        .order_by("-created_at")
    )


def get_active_recommendation_by_slug(*, slug: str):
    return (
        Recommendation.objects
        .filter(is_active=True, slug=slug)
        .prefetch_related(
            "translations",
            Prefetch(
                "recommendation_books",
                queryset=RecommendationBook.objects.select_related("book").order_by("order")
            )
        )
        .order_by("-created_at")
    ).first()
