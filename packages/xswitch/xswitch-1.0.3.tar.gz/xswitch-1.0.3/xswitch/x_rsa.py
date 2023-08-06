from Crypto.PublicKey import RSA

def x_n(p, q):
	return p * q

def x_phi_n(p, q):
	return (p-1) * (q-1)

def x_d(e, phi_n):
	_,x,_ = _extended_gcd(e, phi_n)
	return x % phi_n

def x_priv_key(n, e, d):
	return RSA.construct((n, e, d))

def x_decrypt_msg_hex(msg, key):
	return str(hex(key.decrypt(msg))[2:-1]).decode("hex")

def x_int_to_hex(int):
    return str(hex(int)[2:-1]).decode("hex")

def _extended_gcd(aa, bb):
    lastremainder, remainder = abs(aa), abs(bb)
    x, lastx, y, lasty = 0, 1, 1, 0
    while remainder:
        lastremainder, (quotient, remainder) = remainder, divmod(lastremainder, remainder)
        x, lastx = lastx - quotient*x, x
        y, lasty = lasty - quotient*y, y
    return lastremainder, lastx * (-1 if aa < 0 else 1), lasty * (-1 if bb < 0 else 1)
