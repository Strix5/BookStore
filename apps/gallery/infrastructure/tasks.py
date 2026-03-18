import logging
import os
import subprocess
from pathlib import Path

from celery import shared_task
from django.conf import settings

logger = logging.getLogger(__name__)

HLS_QUALITIES = [
    {"name": "480p",  "height": 480,  "video_bitrate": "1000k", "audio_bitrate": "96k",  "bandwidth": 1150000},
    {"name": "720p",  "height": 720,  "video_bitrate": "2500k", "audio_bitrate": "128k", "bandwidth": 2750000},
    {"name": "1080p", "height": 1080, "video_bitrate": "5000k", "audio_bitrate": "192k", "bandwidth": 5300000},
]

HLS_SEGMENT_DURATION = 6


def _build_ffmpeg_command(
    input_path: str,
    output_dir: Path,
    quality: dict,
) -> list[str]:
    """
    Строит команду ffmpeg для одного качества.

    Зачем выносить в отдельную функцию:
    Список аргументов ffmpeg большой и сложный. Отдельная функция позволяет
    покрыть его юнит-тестом, не запуская реальный ffmpeg.

    Параметры ffmpeg:
    -c:v libx264      — кодек H.264 (максимальная совместимость с HLS-плеерами)
    -c:a aac          — аудиокодек AAC (стандарт для HLS)
    -vf scale         — масштабируем только по высоте; ширина вычисляется автоматически
                        (-2 значит «подобрать чётное число»)
    -hls_time         — длина сегмента в секундах
    -hls_playlist_type vod — плейлист типа VOD (видео по запросу): добавляет #EXT-X-ENDLIST
    -hls_segment_filename — шаблон имён .ts файлов
    -start_number 0   — нумерация сегментов начинается с 0
    """
    quality_dir = output_dir / quality["name"]
    quality_dir.mkdir(parents=True, exist_ok=True)

    segment_pattern = str(quality_dir / "segment%03d.ts")
    playlist_path = str(quality_dir / "index.m3u8")

    return [
        "ffmpeg", "-y",
        "-i", input_path,
        "-c:v", "libx264",
        "-c:a", "aac",
        "-vf", f"scale=-2:{quality['height']}",
        "-b:v", quality["video_bitrate"],
        "-b:a", quality["audio_bitrate"],
        "-hls_time", str(HLS_SEGMENT_DURATION),
        "-hls_playlist_type", "vod",
        "-hls_segment_filename", segment_pattern,
        "-start_number", "0",
        playlist_path,
    ]


def _write_master_playlist(output_dir: Path, produced_qualities: list[dict]) -> Path:
    """
    Создаёт master.m3u8 — главный плейлист HLS, который ссылается на
    плейлисты каждого качества.

    HLS-плеер (hls.js, AVPlayer и т.д.) сначала загружает master.m3u8,
    выбирает подходящее качество по скорости соединения и переключается
    между ними автоматически.

    Зачем relative пути в плейлисте:
    Абсолютные пути привяжут плейлист к конкретному хосту.
    Относительные пути работают корректно через любой CDN или nginx.
    """
    master_path = output_dir / "master.m3u8"
    lines = ["#EXTM3U", "#EXT-X-VERSION:3", ""]

    for quality in produced_qualities:
        lines.append(
            f'#EXT-X-STREAM-INF:BANDWIDTH={quality["bandwidth"]},'
            f'RESOLUTION=x{quality["height"]},'
            f'NAME="{quality["name"]}"'
        )
        # Относительный путь: 480p/index.m3u8
        lines.append(f'{quality["name"]}/index.m3u8')

    master_path.write_text("\n".join(lines), encoding="utf-8")
    return master_path


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_video_to_hls(self, gallery_item_id: int) -> None:
    """
    Celery-таск: конвертирует оригинальное видео в HLS с тремя качествами.

    Зачем bind=True:
    Даёт доступ к self (экземпляру таска), что позволяет:
    - self.retry() — повторить таск при временной ошибке ffmpeg
    - self.request.id — логировать ID таска для отладки

    Зачем max_retries=3, default_retry_delay=60:
    ffmpeg может упасть из-за временной нехватки ресурсов (CPU/диск).
    Три попытки с интервалом 60 секунд покрывают большинство транзиентных сбоев.

    Порядок действий:
    1. Загружаем GalleryItem и проверяем, что оригинальное видео существует.
    2. Ставим статус PROCESSING — API сразу сообщит клиенту что идёт обработка.
    3. Запускаем ffmpeg для каждого качества последовательно.
    4. Пишем master.m3u8.
    5. Сохраняем путь к master.m3u8 в модели, ставим статус READY.
    При любой ошибке — статус FAILED + текст ошибки в hls_error.
    """
    from apps.gallery.infrastructure.models import GalleryItem

    logger.info("[HLS] Starting task %s for GalleryItem #%s", self.request.id, gallery_item_id)

    try:
        item = GalleryItem.objects.get(pk=gallery_item_id)
    except GalleryItem.DoesNotExist:
        logger.error("[HLS] GalleryItem #%s not found. Task aborted.", gallery_item_id)
        return

    if not item.original_video:
        logger.warning("[HLS] GalleryItem #%s has no original_video. Task aborted.", gallery_item_id)
        return

    input_path = os.path.join(settings.MEDIA_ROOT, item.original_video.name)

    if not os.path.isfile(input_path):
        logger.error("[HLS] Original video file not found on disk: %s", input_path)
        _mark_failed(item, f"Original file not found: {input_path}")
        return

    hls_output_dir = Path(settings.MEDIA_ROOT) / "gallery" / "videos" / "hls" / str(item.pk)
    hls_output_dir.mkdir(parents=True, exist_ok=True)

    _mark_processing(item)

    produced_qualities = []

    for quality in HLS_QUALITIES:
        logger.info("[HLS] Converting GalleryItem #%s to %s...", item.pk, quality["name"])

        cmd = _build_ffmpeg_command(input_path, hls_output_dir, quality)

        try:
            subprocess.run(
                cmd,
                check=True,           # бросает CalledProcessError при ненулевом exit code
                capture_output=True,  # перехватываем stdout/stderr ffmpeg
                timeout=1800,         # 30 минут максимум на одно качество
            )
            produced_qualities.append(quality)
            logger.info("[HLS] %s done for GalleryItem #%s.", quality["name"], item.pk)

        except subprocess.CalledProcessError as exc:
            stderr = exc.stderr.decode("utf-8", errors="replace")
            logger.error("[HLS] ffmpeg failed for %s: %s", quality["name"], stderr)
            _mark_failed(item, f"ffmpeg error on {quality['name']}: {stderr[:2000]}")
            # Повторяем таск целиком — не пытаемся частично сохранить результат
            raise self.retry(exc=exc)

        except subprocess.TimeoutExpired:
            logger.error("[HLS] ffmpeg timeout on %s for GalleryItem #%s.", quality["name"], item.pk)
            _mark_failed(item, f"Timeout on {quality['name']}")
            raise self.retry()

    master_path = _write_master_playlist(hls_output_dir, produced_qualities)

    relative_master = master_path.relative_to(settings.MEDIA_ROOT)

    item.hls_master_playlist = str(relative_master)
    item.hls_status = GalleryItem.HLSStatus.READY
    item.hls_error = None
    item.save(update_fields=["hls_master_playlist", "hls_status", "hls_error"])

    logger.info("[HLS] GalleryItem #%s successfully processed. Master: %s", item.pk, relative_master)


def _mark_processing(item) -> None:
    item.hls_status = item.HLSStatus.PROCESSING
    item.hls_error = None
    item.save(update_fields=["hls_status", "hls_error"])


def _mark_failed(item, error_message: str) -> None:
    item.hls_status = item.HLSStatus.FAILED
    item.hls_error = error_message
    item.save(update_fields=["hls_status", "hls_error"])