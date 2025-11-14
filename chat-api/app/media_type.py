import enum

class MediaType(enum.StrEnum):
    # --- Application ---
    APPLICATION_JSON = 'application/json'
    APPLICATION_JAVASCRIPT = 'application/javascript'
    APPLICATION_XML = 'application/xml'
    APPLICATION_XHTML = 'application/xhtml+xml'
    APPLICATION_PDF = 'application/pdf'
    APPLICATION_ZIP = 'application/zip'
    APPLICATION_GZIP = 'application/gzip'
    APPLICATION_TAR = 'application/x-tar'
    APPLICATION_PROTOBUF = 'application/x-protobuf'
    APPLICATION_MSGPACK = 'application/msgpack'
    APPLICATION_FORM_URLENCODED = 'application/x-www-form-urlencoded'
    APPLICATION_OCTET_STREAM = 'application/octet-stream'  # generic binary
    APPLICATION_SQL = 'application/sql'

    # Web API vendor types (commonly used)
    APPLICATION_PROBLEM_JSON = 'application/problem+json'
    APPLICATION_PROBLEM_XML = 'application/problem+xml'
    APPLICATION_JSON_PATCH = 'application/json-patch+json'
    APPLICATION_LD_JSON = 'application/ld+json'

    # --- Text ---
    TEXT_PLAIN = 'text/plain'
    TEXT_HTML = 'text/html'
    TEXT_CSS = 'text/css'
    TEXT_CSV = 'text/csv'
    TEXT_XML = 'text/xml'
    TEXT_MARKDOWN = 'text/markdown'

    # --- Image ---
    IMAGE_JPEG = 'image/jpeg'
    IMAGE_PNG = 'image/png'
    IMAGE_GIF = 'image/gif'
    IMAGE_WEBP = 'image/webp'
    IMAGE_SVG = 'image/svg+xml'
    IMAGE_BMP = 'image/bmp'
    IMAGE_TIFF = 'image/tiff'
    IMAGE_ICON = 'image/x-icon'

    # --- Audio ---
    AUDIO_WAV = 'audio/wav'
    AUDIO_MP3 = 'audio/mpeg'
    AUDIO_OGG = 'audio/ogg'
    AUDIO_AAC = 'audio/aac'
    AUDIO_WEBM = 'audio/webm'

    # --- Video ---
    VIDEO_MP4 = 'video/mp4'
    VIDEO_MPEG = 'video/mpeg'
    VIDEO_OGG = 'video/ogg'
    VIDEO_WEBM = 'video/webm'
    VIDEO_QUICKTIME = 'video/quicktime'

    # --- Multipart ---
    MULTIPART_FORM_DATA = 'multipart/form-data'
    MULTIPART_BYTERANGES = 'multipart/byteranges'