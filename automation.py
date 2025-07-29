import sys

def main():
    # Print all command line arguments except the script name
    args = sys.argv[1:]
    print("Arguments:", args)
    with open('args.txt', 'w') as f:
        for arg in args:
            f.write(arg + '\n')

if __name__ == "__main__":
    main()