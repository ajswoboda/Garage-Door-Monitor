
from relay import relay
def main():
    id = 27
    r = relay(id)
    r.output(True)
    r.output(False)
    r.cleanup()


if __name__ == '__main__':
    main()

