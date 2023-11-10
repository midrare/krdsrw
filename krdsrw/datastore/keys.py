import typing

# timer.average.calculator.distribution.normal
TIMER_AVG_DISTRIBUTION_COUNT: typing.Final[str] = "count"
TIMER_AVG_DISTRIBUTION_SUM: typing.Final[str] = "sum"
TIMER_AVG_DISTRIBUTION_SUM_OF_SQUARES: typing.Final[str] = "sum_of_squares"

# timer.average.calculator
TIMER_AVG_SAMPLES_1: typing.Final[str] = "samples1"
TIMER_AVG_SAMPLES_2: typing.Final[str] = "samples2"
TIMER_AVG_NORMAL_DISTRIBUTIONS: typing.Final[str] = "normal_distributions"
TIMER_AVG_OUTLIERS: typing.Final[str] = "outliers"

# timer.model
TIMER_VERSION: typing.Final[str] = "version"
TIMER_TOTAL_TIME: typing.Final[str] = "total_time"
TIMER_TOTAL_WORDS: typing.Final[str] = "total_words"
TIMER_TOTAL_PERCENT: typing.Final[str] = "total_percent"
TIMER_AVERAGE_CALCULATOR: typing.Final[str] = "average_calculator"

# timer.data.store
TIMERV1_STORE_ON: typing.Final[str] = "on"
TIMERV1_STORE_READING_TIMER_MODEL: typing.Final[str] = "reading_timer_model"
TIMERV1_STORE_VERSION: typing.Final[str] = "version"

# page.history.record
PAGE_HISTORY_POS: typing.Final[str] = "pos"
PAGE_HISTORY_TIME: typing.Final[str] = "time"

# font.prefs
FONT_PREFS_TYPEFACE: typing.Final[str] = "typeface"
FONT_PREFS_LINE_SP: typing.Final[str] = "line_sp"
FONT_PREFS_SIZE: typing.Final[str] = "size"
FONT_PREFS_ALIGN: typing.Final[str] = "align"
FONT_PREFS_INSET_TOP: typing.Final[str] = "inset_top"
FONT_PREFS_INSET_LEFT: typing.Final[str] = "inset_left"
FONT_PREFS_INSET_BOTTOM: typing.Final[str] = "inset_bottom"
FONT_PREFS_INSET_RIGHT: typing.Final[str] = "inset_right"
FONT_PREFS_UNKNOWN_1: typing.Final[str] = "unknown1"
FONT_PREFS_BOLD: typing.Final[str] = "bold"
FONT_PREFS_USER_SIDELOADABLE_FONT: typing.Final[str] = "user_sideloadable_font"
FONT_PREFS_CUSTOM_FONT_INDEX: typing.Final[str] = "custom_font_index"
FONT_PREFS_MOBI_7_SYSTEM_FONT: typing.Final[str] = "mobi7_system_font"
FONT_PREFS_MOBI_7_RESTORE_FONT: typing.Final[str] = "mobi7_restore_font"
FONT_PREFS_READING_PRESET_SELECTED: typing.Final[str
                                                 ] = "reading_preset_selected"

# fpr
FPR_POS: typing.Final[str] = "pos"
FPR_TIMESTAMP: typing.Final[str] = "timestamp"
FPR_TIMEZONE_OFFSET: typing.Final[str] = "timezone_offset"
FPR_COUNTRY: typing.Final[str] = "country"
FPR_DEVICE: typing.Final[str] = "device"

# updated_lpr
UPDATED_LPR_POS: typing.Final[str] = "pos"
UPDATED_LPR_TIMESTAMP: typing.Final[str] = "timestamp"
UPDATED_LPR_TIMEZONE_OFFSET: typing.Final[str] = "timezone_offset"
UPDATED_LPR_COUNTRY: typing.Final[str] = "country"
UPDATED_LPR_DEVICE: typing.Final[str] = "device"

# apnx.key
APNX_ASIN: typing.Final[str] = "asin"
APNX_CDE_TYPE: typing.Final[str] = "cde_type"
APNX_SIDECAR_AVAILABLE: typing.Final[str] = "sidecar_available"
APNX_OPN_TO_POS: typing.Final[str] = "opn_to_pos"
APNX_FIRST: typing.Final[str] = "first"
APNX_UNKNOWN_1: typing.Final[str] = "unknown1"
APNX_UNKNOWN_2: typing.Final[str] = "unknown2"
APNX_PAGE_MAP: typing.Final[str] = "page_map"

# fixed.layout.data
FIXED_LAYOUT_DATA_UNKNOWN_1: typing.Final[str] = "unknown1"
FIXED_LAYOUT_DATA_UNKNOWN_2: typing.Final[str] = "unknown2"
FIXED_LAYOUT_DATA_UNKNOWN_3: typing.Final[str] = "unknown3"

# sharing.limits
SHARING_LIMITS_ACCUMULATED: typing.Final[str] = "accumulated"

# language.store
LANGUAGE_STORE_LANGUAGE: typing.Final[str] = "language"
LANGUAGE_STORE_UNKNOWN_1: typing.Final[str] = "unknown1"

# periodicals.view.state
PERIODICALS_UNKNOWN_1: typing.Final[str] = "unknown1"
PERIODICALS_UNKNOWN_2: typing.Final[str] = "unknown2"

# purchase.state.data
PURCHASE_STATE: typing.Final[str] = "state"
PURCHASE_TIME: typing.Final[str] = "time"

# timer.data.store.v2
TIMERV2_ON: typing.Final[str] = "on"
TIMERV2_READING_TIMER_MODEL: typing.Final[str] = "reading_timer_model"
TIMERV2_VERSION: typing.Final[str] = "version"
TIMERV2_LAST_OPTION: typing.Final[str] = "last_option"

# book.info.store
BOOK_INFO_NUM_WORDS: typing.Final[str] = "num_words"
BOOK_INFO_PERCENT_OF_BOOK: typing.Final[str] = "percent_of_book"

# reader.state.preferences
READER_PREFS_FONT_PREFERENCES: typing.Final[str] = "font_preferences"
READER_PREFS_LEFT_MARGIN: typing.Final[str] = "left_margin"
READER_PREFS_RIGHT_MARGIN: typing.Final[str] = "right_margin"
READER_PREFS_TOP_MARGIN: typing.Final[str] = "top_margin"
READER_PREFS_BOTTOM_MARGIN: typing.Final[str] = "bottom_margin"
READER_PREFS_UNKNOWN_1: typing.Final[str] = "unknown1"

# annotation.personal.bookmark
# annotation.personal.clip_article
# annotation.personal.highlight
# annotation.personal.note
ANNOTATION_START_POS: typing.Final[str] = "start_pos"
ANNOTATION_END_POS: typing.Final[str] = "end_pos"
ANNOTATION_CREATION_TIME: typing.Final[str] = "creation_time"
ANNOTATION_LAST_MODIFICATION_TIME: typing.Final[str] = "last_modification_time"
ANNOTATION_TEMPLATE: typing.Final[str] = "template"
ANNOTATION_NOTE: typing.Final[str] = "note"

# annotation.cache.object
ANNOTATION_BOOKMARKS: typing.Final[int] = 0
ANNOTATION_HIGHLIGHTS: typing.Final[int] = 1
ANNOTATION_NOTES: typing.Final[int] = 2
ANNOTATION_CLIP_ARTICLES: typing.Final[int] = 3
