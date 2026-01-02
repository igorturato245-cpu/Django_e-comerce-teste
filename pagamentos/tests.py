from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch, MagicMock
from pagamentos.models import Pedido
from django.contrib.auth.models import User

class PagSeguroWebhookTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', email='test@example.com', password='testpass123'
        )
        self.pedido = Pedido.objects.create(
            total=10.0, 
            status='pending', 
            payment_reference='PED-1',
            usuario=self.user
        )
    
    def test_notification_without_code(self):
        url = reverse('pagamentos:pagseguro_notify')
        resp = self.client.post(url, data={})
        self.assertEqual(resp.status_code, 400)
    
    @patch('pagamentos.integrations.pagseguro.requests.get')
    def test_notification_paid_status(self, mock_get):
        """
        Testa recebimento de notificação de pagamento APROVADO (Status 3)
        """
        # Simulando resposta XML do PagSeguro
        mock_response = MagicMock()
        mock_response.status_code = 200
        # XML simplificado simulando resposta da API v2/v3
        mock_response.content = b"""
            <Transaction>
                <reference>PED-1</reference>
                <status>3</status>
                <code>TRANS-12345</code>
                <lastEventDate>2023-01-01T12:00:00.000-03:00</lastEventDate>
                <grossAmount>10.00</grossAmount>
                <netAmount>9.50</netAmount>
                <paymentMethod><type>1</type></paymentMethod>
                <installmentCount>1</installmentCount>
            </Transaction>
        """
        mock_get.return_value = mock_response

        url = reverse('pagamentos:pagseguro_notify')
        resp = self.client.post(url, data={'notificationCode': 'any-valid-code'})
        
        self.assertEqual(resp.status_code, 200)
        
        # Verificar se o pedido foi atualizado no banco
        self.pedido.refresh_from_db()
        self.assertEqual(self.pedido.status, 'paid')
        self.assertEqual(self.pedido.metadata['pagseguro_transaction_code'], 'TRANS-12345')

    def test_payment_return_page(self):
        url = reverse('pagamentos:payment_return')
        resp = self.client.get(url, {'reference': 'PED-1', 'status': '3'})
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'PED-1')