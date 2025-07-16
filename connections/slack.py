import requests

from config import settings


class Slack:

    def __init__(self, hook=None):
        self._slack_hook = settings.SLACK_HOOK if (hook is None) else hook

    def send_slack_message(
        self, request_post: dict, message: str = "", warning_type: str = ""
    ):
        """
        Chama a função de criação do `payload` e em seguida a
        função que é responsável por enviar o POST ao Slack

        Args:
            request_post (dict): Model do POST realizado
            message (str, optional): Mensagem que será exibida no Slack
            warning_type (str, optional): Título da mensagem que será exibida
                no Slack
            slack_hook (str, optional): Nome do canal do Slack onde será
                enviada a mensagem
        """
        payload = self.create_slack_post_error(
            request_post=request_post, message=message, warning_type=warning_type
        )
        self.do_slack_post(url_slack=self._slack_hook, payload=payload)

    @staticmethod
    def create_slack_post_error(
        request_post: dict, message: str = "", warning_type: str = ""
    ):
        """
        Função utilizada para gerar o `payload` com a mensagem que será enviada
        para o Slack.

        Args:
            request_post (dict): model do POST realizado
            message (str): Mensagem de warning gerada durante o processamento
            warning_type (str): Título que será exibido na mensagem enviada
                ao Slack

        Returns:
            base_payload (dict): payload necessário para enviar mensagem
            ao Slack
        """

        user_mail = request_post.get("dest_emails", "")
        uuid = request_post.get("uuid", "no uuid found")

        base_payload = {
            "attachments": [
                {
                    "color": "#FF0000",
                    "blocks": [
                        {
                            "type": "header",
                            "text": {
                                "type": "plain_text",
                                "text": warning_type + f": {uuid}",
                            },
                        },
                        {
                            "type": "section",
                            "fields": [
                                {
                                    "type": "mrkdwn",
                                    "text": "*User Info*\n- E-mail: " f"{user_mail}\n",
                                }
                            ],
                        },
                        {
                            "type": "section",
                            "fields": [
                                {"type": "mrkdwn", "text": "*Message*\n%s}" % message}
                            ],
                        },
                    ],
                }
            ]
        }
        return base_payload

    @staticmethod
    def do_slack_post(url_slack, payload):
        """
        Função para realizar um `requests.post` para o
        webhook do channel do Slack com a mensagem de erro.

        Args:
            url_slack (str): url do webhook do canal de destino
            payload (str): JSON formatado para ser enviado ao Slack

        Raises:
            e: Exception caso haja algum problema ao enviar o POST
        """
        try:
            result = requests.post(url_slack, json=payload)

            result.raise_for_status()
        except Exception as e:
            raise e
