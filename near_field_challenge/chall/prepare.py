from mifare import MIFARE, CardNotFoundError
import sys

if __name__ == "__main__":
    mifare = MIFARE()
    if sys.argv[1] == "w":
        mifare.write("guest:guest")
    else:
        print mifare.read()
