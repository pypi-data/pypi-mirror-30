def find_between(s, first, last):
    try:
        start = s.index(first)+len(first)
        end = s.index(last, start)
        return s[start:end]
    except ValueError:
        return ""


def find_until(s, until):
    try:
        until = s.index(until)
        return s[0:until]
    except ValueError:
        return ""


def get_correctly_extended_latex_label(label, label_extension):
    if '^{' in label and '^{' in label_extension:
        return label[:-1] + ',' + label_extension[2:]
    else:
        return label + label_extension
