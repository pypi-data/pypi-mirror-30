import requests
import blockcypher
#import environ
from django.db import models
from django.conf import settings
from django.urls import reverse
from django.core import signing

from django.utils.functional import cached_property
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.fields import GenericRelation

from model_utils import Choices, FieldTracker
from model_utils.models import TimeStampedModel, SoftDeletableModel
from model_utils.fields import StatusField, MonitorField
#env = environ.Env()
#domain = env('DOMAIN_NAME', default='stagingserver.xyz')
#api_key = env('BLOCKCYPHER_API_KEY')
domain = settings.DOMAIN_NAME
api_key = settings.BLOCKCYPHER_API_KEY
#domain = settings.DOMAIN_NAME
#api_key = settings.BLOCKCYPHER_API_KEY
from django.core.validators import MinValueValidator


@python_2_unicode_compatible
class BaseWallet(TimeStampedModel, SoftDeletableModel):

    private = models.CharField(max_length=150, unique=True)
    public = models.CharField(max_length=150, unique=True)
    address = models.CharField(max_length=150, unique=True)
    wif = models.CharField(max_length=150, unique=True)

    received_invoices = GenericRelation('wallets.Invoice')
    sended_invoices = GenericRelation('wallets.Invoice')

    class Meta:
        abstract = True

    def __str__(self):
        return '({}) {}'.format(
            self.coin_symbol.upper(), 
            self.address
            )

    def get_absolute_url(self):
        return reverse('wallets:detail', kwargs={'wallet': self.coin_symbol, 'address': self.address})

    def spend(self, address, amount):
        new_transaction = blockcypher.simple_spend(
            from_privkey=self.private,
            to_address=address,
            to_satoshis=amount, 
            coin_symbol=self.coin_symbol,
            api_key=settings.BLOCKCYPHER_API_KEY
        )
        return new_transaction

    def spend_with_webhook(self, address, amount):
        new_transaction = blockcypher.simple_spend(
            from_privkey=self.private,
            to_address=address,
            to_satoshis=amount, 
            coin_symbol=self.coin_symbol,
            api_key=settings.BLOCKCYPHER_API_KEY
        )        
        self.set_webhook(to_address=address, transaction=new_transaction, event='confirmed-tx')
        return new_transaction

    def set_webhook(self, to_address, transaction, event='confirmed-tx'):
        signature = signing.dumps({
            'from_address': self.address,
            'to_address': to_address,
            'symbol': self.coin_symbol,
            'event': event,
            'transaction_id': transaction
            })
        webhook = blockcypher.subscribe_to_address_webhook(
            callback_url='https://{}/wallets/webhook/{}/'.format(domain, signature),
            subscription_address=self.address,
            event=event,
            coin_symbol=self.coin_symbol,
            api_key=settings.BLOCKCYPHER_API_KEY
        )
        return webhook

    @property
    def rate(self):
        response = requests.get('https://api.coinmarketcap.com/v1/ticker/{}/'.format(self.coin_name))
        json_response = response.json()
        return json_response[0]['price_usd']

    @cached_property
    def address_details(self):
        return blockcypher.get_address_details(self.address, coin_symbol=self.coin_symbol)

    @cached_property
    def overview(self):
        return blockcypher.get_address_overview(self.address, coin_symbol=self.coin_symbol)

    @cached_property
    def balance(self):
        overview = self.overview
        return overview['balance']

    @cached_property
    def transactions(self):
        get_address_full = self.address_details
        return get_address_full['txrefs']

    @staticmethod
    def transaction_details(tx_ref, coin_symbol='btc'):
        return blockcypher.get_transaction_details(tx_ref, coin_symbol)

    def create_invoice(self, wallet, amount, content_object):
        invoice = Invoice.objects.create(
            amount = amount,
            receiver_wallet_object = wallet,
            sender_wallet_object = self,
            content_object = content_object
        )
        return invoice


@python_2_unicode_compatible
class Btc(BaseWallet):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="btc_wallets", on_delete=models.CASCADE)
    coin_symbol = models.CharField(max_length=5, default='btc')
    coin_name = models.CharField(max_length=10, default='bitcoin')

    @cached_property
    def total_balance(self):
        balance = 0
        for address in self.user.btc_wallets.all():
            balance += address.balance
        return balance


@python_2_unicode_compatible
class Doge(BaseWallet):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="doge_wallets", on_delete=models.CASCADE)
    coin_symbol = models.CharField(max_length=5, default='doge')
    coin_name = models.CharField(max_length=10, default='dogecoin')

    @cached_property
    def total_balance(self):
        balance = 0
        for address in self.user.doge_wallets.all():
            balance += address.balance
        return balance


@python_2_unicode_compatible
class Ltc(BaseWallet):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="ltc_wallets", on_delete=models.CASCADE)
    coin_symbol = models.CharField(max_length=5, default='ltc')
    coin_name = models.CharField(max_length=10, default='litecoin')

    @cached_property
    def total_balance(self):
        balance = 0
        for address in self.user.ltc_wallets.all():
            balance += address.balance
        return balance


@python_2_unicode_compatible
class Dash(BaseWallet):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="dash_wallets", on_delete=models.CASCADE)
    coin_symbol = models.CharField(max_length=5, default='dash')
    coin_name = models.CharField(max_length=10, default='dash')

    @cached_property
    def total_balance(self):
        balance = 0
        for address in self.user.dash_wallets.all():
            balance += address.balance
        return balance


@python_2_unicode_compatible
class Bcy(BaseWallet):

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="bcy_wallets", on_delete=models.CASCADE)
    coin_symbol = models.CharField(max_length=5, default='bcy')
    coin_name = models.CharField(max_length=10, default='bcy')

    @property
    def rate(self):
        return 0

    @cached_property
    def total_balance(self):
        balance = 0
        for address in self.user.bcy_wallets.all():
            balance += address.balance
        return balance        


@python_2_unicode_compatible
class Invoice(models.Model):

    limit = models.Q(app_label='wallets', model='btc') | \
            models.Q(app_label='wallets', model='ltc') | \
            models.Q(app_label='wallets', model='dash') | \
            models.Q(app_label='wallets', model='doge') | \
            models.Q(app_label='wallets', model='bcy')

    amount = models.BigIntegerField(validators=[MinValueValidator(0)])

    receiver_wallet_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, limit_choices_to=limit, related_name='received_invoices')
    receiver_wallet_id = models.PositiveIntegerField()
    receiver_wallet_object = GenericForeignKey('receiver_wallet_type', 'receiver_wallet_id')

    sender_wallet_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, limit_choices_to=limit, related_name='sended_invoices')
    sender_wallet_id = models.PositiveIntegerField()
    sender_wallet_object = GenericForeignKey('sender_wallet_type', 'sender_wallet_id')

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, related_name='invoies_objects')
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    is_paid = models.BooleanField(default=False)


    def __init__(self, *args, **kwargs):
        super(Invoice, self).__init__(*args, **kwargs)
        self.__important_fields = ['is_paid']
        for field in self.__important_fields:
            setattr(self, '__original_%s' % field, getattr(self, field))

    def has_changed(self):
        for field in self.__important_fields:
            orig = '__original_%s' % field
            if getattr(self, orig) != getattr(self, field):
                return True
        return False

    def pay(self):
        tx_ref = self.sender_wallet_object.spend(
            self.sender_wallet_object.address,
            self.amount
            )
        invoice_transaction = InvoiceTransaction.objects.create(invoice = self, tx_ref = tx_ref)
        return invoice_transaction.tx_ref

    def get_absolute_url(self):
       return reverse('wallets:invoice_detail', kwargs={'pk': self.pk})
    
    def can_be_confirmed(self):
        if self.tx_refs.all():
            tx_refs_total_amount = 0
            for tx in self.tx_refs.all():
                details = blockcypher.get_transaction_details(
                    tx.tx_ref,
                    self.sender_wallet_object.coin_symbol
                )
                tx_refs_total_amount += details['outputs'][0]['value']

            assert int(self.amount) < tx_refs_total_amount, 'Invoice can be confirmed, because the amount of all transactions is less than the amount of the invoice.'        
            
            return True
        return False
    
    def save(self, *args, **kwargs):
        self.full_clean()
        has_changed = self.has_changed()
        if has_changed:
            self.can_be_confirmed()
        return super(Invoice, self).save(*args, **kwargs)


@python_2_unicode_compatible
class InvoiceTransaction(models.Model):

    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='tx_refs')
    tx_ref = models.CharField(max_length=100, null=True, blank=False)

    is_confirmed = models.BooleanField(default=False)

    def __str__(self):
        return self.tx_ref