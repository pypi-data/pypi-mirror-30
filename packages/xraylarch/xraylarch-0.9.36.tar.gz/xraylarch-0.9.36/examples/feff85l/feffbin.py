from padlib import unpad, read_pad_float, read_pad_complex

def read_feffpad(filename='feff.pad'):
    """
    read feff.pad file, return list of Feff path data
    """
    out = []
    with open(filename, 'r') as fh:
        text = fh.readlines()

        # first line, must match  "#_feff.pad v03"
        line = text.pop(0).strip()
        if not line.startswith('#_feff.pad v03'):
            raise IOError('read_feffpad error: not a valid FEFF PAD file')

        # next line: npot, ne
        line = text.pop(0).strip()
        if not line.startswith('#_'):
            raise IOError('read_feffpad error: not a valid FEFF PAD file')
        words = line[2:].split()
        if len(words) != 3:
            raise IOError('read_feffpad error: missing data')
        npot, ne, npack = [int(s) for s in words]

        # next line: ihole, iorder, ilinit, rnrmav, xmu, edge
        line = text.pop(0).strip()
        if not line.startswith('#&'):
            raise IOError('read_feffpad error: not a valid FEFF PAD file')
        words = line[2:].split()
        if len(words) != 6:
            raise IOError('read_feffpad error: missing data')
        ihole, iorder, ilinit = [int(s) for s in words[:3]]
        rnorm, xmu, edge      = [float(s) for s in words[3:]]

        # next line: labels and iz
        line = text.pop(0).strip()
        if not line.startswith('#@'):
            raise IOError('read_feffpad error: not a valid FEFF PAD file')
        words = line[2:].split()
        if len(words) != 2*(npot+1):
            raise IOError('read_feffpad error: missing data')
        pot_labels = [s for s in words[:npot+1]]
        pot_iz     = [int(s) for s in words[npot+1:]]

        phc = read_pad_float(text, ne, npack=npack)
        c
