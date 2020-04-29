import pytest
from channels.layers import get_channel_layer
from channels.testing import WebsocketCommunicator

from exlibris.consumers import ChatConsumer


@pytest.mark.asyncio
async def test_chat_consumer():
    communicator = WebsocketCommunicator(ChatConsumer, '/ws/chat')
    connected, _ = await communicator.connect()
    assert connected
    response = await communicator.receive_json_from()
    assert response['message'] == '# ws connection established'

    message = 'Wed Apr 29 21:50:46 2020 '\
        '№1 Гарри Поттер и узник Азкабана; '\
        '№2 Зеленая миля; '\
        '№3 Унесенные ветром; '\
        '№4 Прислуга; '\
        '№5 Граф Монте-Кристо'
    channel_layer = get_channel_layer()
    await channel_layer.group_send(
        'chat_default',
        {
            'type': 'chat_message',
            'message': message,
        }
    )
    response = await communicator.receive_json_from()
    assert response['message'] == message

    await communicator.disconnect()