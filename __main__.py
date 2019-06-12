from mailscan.scanner import Scanner


def run_scanner():
    addr = input('With which address we start with? ')
    if 'http' not in addr:
        addr = f"http://{addr}"

    s = Scanner(addr)
    s.scan()

    print('READY! You\'ll find found addresses in mails.txt file')
    exit(0)


if __name__ == "__main__":
    run_scanner()
