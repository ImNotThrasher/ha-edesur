"""Constants shared by the Edesur integration."""
from datetime import timedelta

DOMAIN = "edesur"
API_BASE_URL = "https://ed.edesur.com.ar/api"
ORIGIN_CHANNEL = "Wbns-RgKfqY~"
UPDATE_INTERVAL = timedelta(hours=6)
CONF_AUTH_METHOD = "auth_method"
CONF_SOCIAL_ID = "social_id"
AUTH_GOOGLE = "google"
