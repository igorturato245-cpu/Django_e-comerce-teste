# Integração PagSeguro + ERP

## Visão Geral
Este sistema integra pagamentos via PagSeguro com sincronização de pedidos para um ERP externo.

## Endpoints Importantes

### PagSeguro
- **Webhook**: `/pagamentos/notifications/` (POST)
- **Iniciar pagamento**: `/pagamentos/start/` (GET/POST)
- **Retorno após pagamento**: `/pagamentos/return/` (GET)

### ERP
- **Buscar produtos**: `GET ${ERP_API_URL}/products`
- **Verificar disponibilidade**: `GET ${ERP_API_URL}/products/{id}/availability`
- **Enviar pedido**: `POST ${ERP_API_URL}/orders`

## Fluxo de Pagamento

1. **Adição ao Carrinho**
   - Valida estoque no ERP em tempo real
   - Atualiza cache local
   - Adiciona produto ao carrinho

2. **Checkout**
   - Cria pedido no sistema local
   - Gera checkout no PagSeguro
   - Redireciona usuário para PagSeguro

3. **Pagamento**
   - Usuário paga no PagSeguro
   - PagSeguro envia notificação para webhook

4. **Processamento**
   - Sistema valida notificação
   - Atualiza status do pedido
   - Se pago, envia para fila do ERP

5. **ERP Integration**
   - Task assíncrona envia pedido para ERP
   - Atualiza status com resposta do ERP
   - Retry em caso de falha

## Segurança
- Validar origem da notificação PagSeguro
- Confirmar status via API antes de atualizar pedido
- Nunca confiar apenas no payload recebido

## Processamento Assíncrono
- Envio de pedidos ao ERP ocorre via Celery
- Retry automático configurado
- Falhas são logadas

## Configuração

### Variáveis de Ambiente Necessárias

> ⚠️ **Nunca versionar valores reais dessas variáveis.**

```env
# ERP
ERP_API_URL={ERP_API_URL}
ERP_API_KEY={ERP_API_KEY}
ERP_TIMEOUT=10

# PagSeguro
PAGSEGURO_EMAIL={PAGSEGURO_EMAIL}
PAGSEGURO_TOKEN={PAGSEGURO_TOKEN}
PAGSEGURO_SANDBOX=true
