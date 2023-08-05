#!/usr/bin/env python
from pkcrypt import *


def test():
    xsk = keys.gen_private_key(curve.P256)
    ssk = sk2str(xsk)

    sk = str2sk(ssk)

    xvk = keys.get_public_key(sk, curve.P256)
    svk = vk2str( xvk )

    vk = str2vk(svk)

    msg = "a message to sign via ECDSA"  # some message

    rs = ecdsa.sign(msg, sk)

    ssig = sig2str(rs)

    sig = str2sig(ssig)

    valid = ecdsa.verify(rs, msg, vk)
    if not valid: exit(1)

    valid = ecdsa.verify(sig, msg, vk)
    if not valid: exit(1)


if __name__ == '__main__': test()
