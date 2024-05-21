import tiktoken
import argparse
import os

def count_tokens(text, encoding_name='cl100k_base'):
    """
    Counts the number of tokens in the given text for the specified encoding.

    :param text: The input text to count tokens.
    :param encoding_name: The encoding to use for token counting. Default is 'cl100k_base'.
    :return: The number of tokens in the text.
    """
    encoder = tiktoken.get_encoding(encoding_name)
    tokens = encoder.encode(text)
    return len(tokens)

def count_tokens_in_file(file_path, encoding_name='cl100k_base'):
    """
    Reads the text from the given file and counts the number of tokens.

    :param file_path: Path to the file to read.
    :param encoding_name: The encoding to use for token counting. Default is 'cl100k_base'.
    :return: The number of tokens in the file.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    return count_tokens(text, encoding_name)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Count tokens in text files.")
    parser.add_argument('files', metavar='F', type=str, nargs='+', help='Paths to the text files to process.')
    parser.add_argument('--encoding', type=str, default='cl100k_base', help='Encoding to use for token counting (default: cl100k_base).')

    args = parser.parse_args()

    for file_path in args.files:
        if os.path.isfile(file_path):
            token_count = count_tokens_in_file(file_path, args.encoding)
            print(f"{file_path}: {token_count} tokens")
        else:
            print(f"Error: File not found - {file_path}")
