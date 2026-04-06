output_file = None


def set_output(file_path):
    global output_file
    output_file = file_path

    with open(output_file, "w") as f:
        f.write("[+] Scan Results\n\n")


def save(data):
    if output_file:
        with open(output_file, "a") as f:
            f.write(data + "\n")
