
class ManufEntry:
    def __init__(self, prefix, prefix_len, manuf, desc):
        self.prefix = prefix
        self.prefix_len = prefix_len
        self.manuf = manuf
        self.desc = desc

class ManufDatabase:
    def __init__(self, file_path):
        self.entries = {}
        # FIXME: Move the parsing / file loading into a private helper function.
        with open(file_path, "r") as handle:
            for line in handle.readlines():
                if line.startswith("#") or line == "\n":
                    continue
                values = line.split("\t")
                if len(values) < 2:
                    raise ValueError("Required at least 2 values")
                prefix = values[0]
                manuf = values[1].strip()
                try:
                    desc = values[2]
                except IndexError:
                    desc = ""
                prefix = prefix.replace(":", "")
                prefix_len = 24
                if "/" in prefix:
                    [ prefix, prefix_len ] = prefix.split("/")
                    prefix_len = int(prefix_len)
                prefix = int(prefix, base=16)
                entry = ManufEntry(prefix, prefix_len, manuf, desc)
                self.entries[prefix] = entry
    def query(self, mac_addr, prefix_len=24):
        # TODO: Handle non-24 bit prefix lengths here.
        mac_addr = mac_addr.replace(":", "")
        mac_addr = int(mac_addr, base=16)
        mac_addr = mac_addr >> (48 - prefix_len)
        try:
            return self.entries[mac_addr]
        except KeyError:
            return None

def main():
    manuf_db = ManufDatabase("manuf.txt")
    print(manuf_db.query(input("Enter MAC Address: ")).manuf)

if __name__ == "__main__":
    main()
