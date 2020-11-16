from switch import switch

def main():
    gpioDict = {
                'open' : 17
    }
    s = switch(gpioDict)
    s.monitor()



if __name__ == '__main__':
    main()


