from chainsync.adapters.abstract import AbstractAdapter
from chainsync.adapters.base import BaseAdapter
from chainsync.utils.http_client import HttpClient

from jsonrpcclient.request import Request

class SteemAdapter(AbstractAdapter, BaseAdapter):

    config = {
        'BLOCK_INTERVAL': 'STEEMIT_BLOCK_INTERVAL',
        'HEAD_BLOCK_NUMBER': 'head_block_number',
        'LAST_IRREVERSIBLE_BLOCK_NUM': 'last_irreversible_block_num',
        'VIRTUAL_OPS': [
            'fill_convert_request',
            'author_reward',
            'curation_reward',
            'comment_reward',
            'liquidity_reward',
            'interest',
            'fill_vesting_withdraw',
            'fill_order',
            'shutdown_witness',
            'fill_transfer_from_savings',
            'hardfork',
            'comment_payout_update',
            'return_vesting_delegation',
            'comment_benefactor_reward',
            'producer_reward',
        ]
    }

    def format_op_from_get_block(self, block, op, txIndex=False, opIndex=False):
        opType, opData = op
        opData['block_num'] = block['block_num']
        opData['op_in_trx'] = opIndex
        opData['operation_type'] = opType
        opData['timestamp'] = block['timestamp']
        opData['transaction_id'] = block['transaction_ids'][txIndex]
        opData['trx_in_block'] = txIndex
        return opData

    def format_op_from_get_ops_in_block(self, op):
        opType, opData = op['op']
        opData['block_num'] = op['block']
        opData['op_in_trx'] = op['op_in_trx']
        opData['operation_type'] = opType
        opData['timestamp'] = op['timestamp']
        opData['transaction_id'] = op['trx_id']
        opData['trx_in_block'] = op['trx_in_block']
        return opData

    def format_op_from_get_transaction(self, tx, op, txIndex=False, opIndex=False):
        opType, opData = op
        opData['block_num'] = tx['block_num']
        opData['op_in_trx'] = opIndex
        opData['operation_type'] = opType
        opData['timestamp'] = False
        opData['transaction_id'] = tx['transaction_id']
        opData['trx_in_block'] = txIndex
        return opData

    def get_block(self, block_num):
        response = HttpClient(self.endpoint).request('get_block', [block_num])
        try:
            response['block_num'] = int(str(response['block_id'])[:8], base=16)
        except KeyError as e:
            print(e)
            print(response)
        return response

    def get_blocks(self, blocks):
        for i in blocks:
            yield self.call('get_block', block_num=int(i))

    def get_config(self):
        return HttpClient(self.endpoint).request('get_config')

    def get_methods(self):
        return 'NOT_SUPPORTED'

    def get_ops_in_block(self, block_num, virtual_only=False):
        return HttpClient(self.endpoint).request('get_ops_in_block', [block_num, virtual_only])

    def get_ops_in_blocks(self, blocks, virtual_only=False):
        for i in blocks:
            yield self.call('get_ops_in_block', block_num=i, virtual_only=virtual_only)

    def get_status(self):
        return HttpClient(self.endpoint).request('get_dynamic_global_properties')

    def get_transaction(self, transaction_id=1):
        response = HttpClient(self.endpoint).request('get_transaction', [transaction_id])
        try:
            response['block_num'] = int(str(response['block_id'])[:8], base=16)
        except KeyError as e:
            pass
        return response

    def get_transactions(self, transaction_ids=[]):
        for transaction_id in transaction_ids:
            yield self.call('get_transaction', transaction_id=transaction_id)
