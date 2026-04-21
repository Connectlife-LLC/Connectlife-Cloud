"""Constants for ConnectLife Cloud API client."""

# API credentials
CLIENT_ID = "9793620883275788"
CLIENT_SECRET = "7h1m3gZVlILyBvIFBNmzXwoFYLhkGqG9NQd2jBzuZCqJKCTyCtYwQtXi4tVBjg9B"


# Production environment OAuth2 and API configuration
OAUTH2_AUTHORIZE = "https://oauth.hijuconn.com/login"
OAUTH2_TOKEN = "https://oauth.hijuconn.com/oauth/token"
WEBSOCKET_URL = "wss://clife-eu-gateway.hijuconn.com/msg/get_msg_and_channels"
API_BASE_URL = "https://juapi-3rd.hijuconn.com"

# API Endpoints
API_DEVICE_LIST = "/clife-svc/pu/get_device_status_list"
API_GET_PROPERTY_LTST = "/clife-svc/get_property_list"  # Get device property list
API_QUERY_STATIC_DATA = (
    "/clife-svc/pu/query_static_data"  # Get device property list using puId
)
API_DEVICE_CONTROL = "/device/pu/property/set"
API_SELF_CHECK = "/basic/self_check/info"  # Get fault information
API_GET_HOUR_POWER = "/clife-svc/pu/get_hour_power"  # Get power consumption information
