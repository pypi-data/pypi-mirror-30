
def generate_address_csv(addresses, address_type, include_header, settings):

    output = []

    if address_type == "business":
        header = settings.file_formats["business_header"]
        format_string = settings.file_formats["business"]
    else:
        header = settings.file_formats["standard_header"]
        format_string = settings.file_formats["standard"]

    if include_header is True:
        output.append(header)

    for address in addresses:
        if address_type == "business":
            result = str.format(format_string, address.recipient, address.address_line_1, address.address_line_2,
                                address.city, address.state, address.zip_code).replace('\n', '')
            output.append(result)
        else:
            result = str.format(format_string, address.recipient, address.address_line_1, address.city,
                                address.state, address.zip_code).replace('\n', '')
            output.append(result)

    return output
