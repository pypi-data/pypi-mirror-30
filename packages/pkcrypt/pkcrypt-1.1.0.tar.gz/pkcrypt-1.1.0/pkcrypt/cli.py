#!/usr/bin/env python
from pkcrypt import *

def decode_cli():
    key = sys.stdin.readline()
    encoded_text = sys.stdin.read().encode()
    _, decoded_text = decode(key, encoded_text)
    sys.stdout.write(decoded_text.decode())

def encode_cli():
    key = Fernet.generate_key() #this is your "password"
    cipher_suite = Fernet(key)
    decoded_text = sys.stdin.read().encode()
    key, encoded_text = encode(key, decoded_text)
    print(key.decode())
    print(encoded_text.decode())

def usage():
    print("BAD ARGS")
    print("Try one of: genpair, gensk, getvk, sign, verify")
    raise exit(2)
    
def cli(argv=sys.argv):
    eol, fname = '\n', ''

    def getarg2(name):
        try:
            if sys.argv[2] == name:
                sys.argv.pop(2)
                return 1
        except:
            return

    def output(msg, _eol = None):
        if _eol is None: _eol = eol
        with open(fname,'w') if fname else sys.stdout as f:
            f.write(msg + _eol)

    if getarg2('-no'): eol = ''; fname = sys.argv.pop(2)
    if getarg2('-n'):  eol = ''
    if getarg2('-o'):            fname = sys.argv.pop(2)

    try:
        arg1 = sys.argv[1]
    except IndexError:
        return usage()

    if   arg1 == 'gensk':
        output(sk2str(gen_sk()))
    elif arg1 == 'getvk':
        output(vk2str(get_vk(fload_sk())))
    elif arg1 == 'genpair':
        output('%s\n%s' % gen_keys())
    elif arg1 == 'sign':
        msg = load_msg()
        sgn = sig2str(sign_with(fload_sk(), msg))
        if sys.argv[-1] == '-h':
            sgn += '\n' + msg
            output(sgn, '')
        else:            
            output(sgn)
    elif arg1 == 'verify':
        try:
            if invalid_sig(fload_vk(), load_sig(), load_msg()):
                print("NOT VALID: MISMATCH")
                exit(1)
        except SystemExit:
            raise
        except:
            print("NOT VALID: FORMAT ERROR")
            exit(1)
    else:
        return usage()

if __name__ == '__main__': cli()
