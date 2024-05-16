from amocrm.v2 import tokens
from .models import AmoCRMToken


class DatabaseTokensStorage(tokens.TokensStorage):
    def __init__(self):
        super().__init__()

    def save_tokens(self, client_id, tokens_data):
        AmoCRMToken.objects.update_or_create(
            client_id=client_id,
            defaults={
                'access_token': tokens_data.get('access_token', ''),
                'refresh_token': tokens_data.get('refresh_token', '')
            }
        )

    def load_tokens(self, client_id):
        try:
            token = AmoCRMToken.objects.get(client_id=client_id)
            return {
                'access_token': token.access_token,
                'refresh_token': token.refresh_token
            }
        except AmoCRMToken.DoesNotExist:
            return None
