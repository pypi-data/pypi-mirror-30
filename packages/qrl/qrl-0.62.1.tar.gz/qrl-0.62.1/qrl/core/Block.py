# coding=utf-8
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php.
from google.protobuf.json_format import MessageToJson, Parse

from qrl.core import config
from qrl.core.misc import logger
from qrl.core.Transaction import CoinBase, Transaction
from qrl.core.BlockHeader import BlockHeader
from qrl.crypto.misc import sha256, merkle_tx_hash
from qrl.generated import qrl_pb2


class Block(object):
    def __init__(self, protobuf_block=None):
        self._data = protobuf_block
        if protobuf_block is None:
            self._data = qrl_pb2.Block()

        self.blockheader = BlockHeader(self._data.header)

    @property
    def size(self):
        return self._data.ByteSize()

    @property
    def pbdata(self):
        """
        Returns a protobuf object that contains persistable data representing this object
        :return: A protobuf Block object
        :rtype: qrl_pb2.Block
        """
        return self._data

    @property
    def block_number(self):
        return self.blockheader.block_number

    @property
    def epoch(self):
        return int(self.block_number // config.dev.blocks_per_epoch)

    @property
    def headerhash(self):
        return self.blockheader.headerhash

    @property
    def prev_headerhash(self):
        return self.blockheader.prev_blockheaderhash

    @property
    def transactions(self):
        return self._data.transactions

    @property
    def mining_nonce(self):
        return self.blockheader.mining_nonce

    @property
    def PK(self):
        return self.blockheader.PK

    @property
    def block_reward(self):
        return self.blockheader.block_reward

    @property
    def fee_reward(self):
        return self.blockheader.fee_reward

    @property
    def timestamp(self):
        return self.blockheader.timestamp

    @property
    def mining_blob(self)->bytes:
        return self.blockheader.mining_blob

    @property
    def mining_nonce_offset(self)->bytes:
        return self.blockheader.nonce_offset

    @staticmethod
    def from_json(json_data):
        pbdata = qrl_pb2.Block()
        Parse(json_data, pbdata)
        return Block(pbdata)

    def verify_blob(self, blob: bytes) -> bool:
        return self.blockheader.verify_blob(blob)

    def set_mining_nonce(self, mining_nonce):
        self.blockheader.set_mining_nonce(mining_nonce)

    def to_json(self)->str:
        # FIXME: Remove once we move completely to protobuf
        return MessageToJson(self._data)

    @staticmethod
    def create(block_number: int,
               prevblock_headerhash: bytes,
               transactions: list,
               miner_address: bytes):

        block = Block()

        # Process transactions
        hashedtransactions = []
        fee_reward = 0

        for tx in transactions:
            fee_reward += tx.fee

        # Prepare coinbase tx
        total_reward_amount = BlockHeader.block_reward_calc(block_number) + fee_reward
        coinbase_tx = CoinBase.create(total_reward_amount, miner_address, block_number)
        hashedtransactions.append(coinbase_tx.txhash)
        block._data.transactions.extend([coinbase_tx.pbdata])  # copy memory rather than sym link

        for tx in transactions:
            hashedtransactions.append(tx.txhash)
            block._data.transactions.extend([tx.pbdata])  # copy memory rather than sym link

        if not hashedtransactions:
            hashedtransactions = [sha256(b'')]

        txs_hash = merkle_tx_hash(hashedtransactions)           # FIXME: Find a better name, type changes

        tmp_blockheader = BlockHeader.create(blocknumber=block_number,
                                             prev_blockheaderhash=prevblock_headerhash,
                                             hashedtransactions=txs_hash,
                                             fee_reward=fee_reward)

        block._data.header.MergeFrom(tmp_blockheader.pbdata)

        block.set_mining_nonce(0)

        return block

    def validate(self) -> bool:
        fee_reward = 0
        for index in range(1, len(self.transactions)):
            fee_reward += self.transactions[index].fee

        if len(self.transactions) == 0:
            return False

        try:
            coinbase_txn = Transaction.from_pbdata(self.transactions[0])
            coinbase_amount = coinbase_txn.amount
        except Exception as e:
            logger.warning('Exception %s', e)
            return False

        return self.blockheader.validate(fee_reward, coinbase_amount)

    def validate_parent_child_relation(self, parent_block) -> bool:
        return self.blockheader.validate_parent_child_relation(parent_block)

    def add_transaction(self, tx: Transaction):
        # TODO: Verify something basic here?
        self._data.transactions.extend(tx.pbdata)
