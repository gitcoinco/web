struct Channel:
   id: bytes32
   value: wei_value
   host: address
   hostDelegate: address
   guest: address
   guestDelegate: address
   open: bool
   expires: uint256  # block number after which host can cancel the session


ChannelOpened: event({
    id: bytes32
})

ChannelClosed: event({
    id: bytes32,
    value: wei_value  # Value claimed by guest
})

LogAddress: event({a: address})
LogBytes: event({a: bytes32})

channels: public(map(bytes32, Channel))  # delegate address -> main address
balances: public(map(bytes32, wei_value)) # main address -> wei balance


@payable
@public
def createChannel(
    hostDelegateAddress: address,
    guestMainAddress: address,
    guestDelegateAddress: address,
    guestSignature: uint256[3],
    lockInterval: uint256,
    ):

    h1: bytes32 = sha3("join")
    h2: bytes32 = sha3(concat(b"\x19Ethereum Signed Message:\n32", h1))
    assert guestDelegateAddress == ecrecover(h2, guestSignature[0], guestSignature[1], guestSignature[2])

    channel: Channel = Channel({
        id: sha3(concat(
            convert(block.timestamp, bytes32),
            convert(msg.sender, bytes32),
            convert(guestMainAddress, bytes32)
        )),
        value: msg.value,
        host: msg.sender,
        hostDelegate: hostDelegateAddress,
        guest: guestMainAddress,
        guestDelegate: guestDelegateAddress,
        open: True,
        expires: block.number + lockInterval
    })
    self.channels[channel.id] = channel
    log.ChannelOpened(channel.id)


@public
def closeChannel(
    channelId: bytes32,
    value: wei_value,
    hostDelegateSignature: uint256[3]
    ):

    # get game
    # check channel is open
    assert self.channels[channelId].open == True

    log.LogAddress(self.channels[channelId].hostDelegate)
    log.LogAddress(self.channels[channelId].guest)
    log.LogAddress(msg.sender)
    # check msg.sender is guest
    assert self.channels[channelId].guest == msg.sender

    # check message was signed by hostDelegate
    h1: bytes32 = sha3(concat(
        channelId,
        convert(b"close_channel", bytes32),
        convert(value, bytes32),
    ))

    h2: bytes32 = sha3(concat(b"\x19Ethereum Signed Message:\n32", h1))
    log.LogAddress(ecrecover(
        h2,
        hostDelegateSignature[0],
        hostDelegateSignature[1],
        hostDelegateSignature[2]
    ))

    log.LogBytes(convert(b"close_channel", bytes32))
    log.LogBytes(channelId)
    log.LogBytes(h1)

    assert self.channels[channelId].hostDelegate == ecrecover(
        h2,
        hostDelegateSignature[0],
        hostDelegateSignature[1],
        hostDelegateSignature[2]
    )


    # check guest is requesting a valid amount
    assert self.channels[channelId].value >= value

    self.channels[channelId].open = False

    # transfer amount to guest
    refundAmount: wei_value = self.channels[channelId].value - value

    # TODO use withdraw pattern
    send(msg.sender, value)
    send(self.channels[channelId].host, refundAmount)

    log.ChannelClosed(channelId, value)


























