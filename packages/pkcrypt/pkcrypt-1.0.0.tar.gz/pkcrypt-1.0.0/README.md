# pkcrypt

## public key crypto

```
python3 -m pkcrypt genpair >p ; echo $?

# the first line is your public key
# the second line is your private key

python3 -m pkcrypt sign p -h <Makefile >s2 ; echo $?

python3 -m pkcrypt verify p <s2 ; echo $?

```

