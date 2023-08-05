from __future__ import print_function
import liam

CREDS = {
    'aws_access_key_id': "AKIAIYBZLNK2QMURGWAA",
    'aws_secret_access_key': "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"
}


def main():
    scanner = liam.Scanner(CREDS)
    results = scanner.full_scan()
    print(results)


if __name__ == '__main__':
    main()
