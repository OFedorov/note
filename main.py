from note import Repository, Note, NoteMeta

class Config:
    def __init__(self, db_path="", table_name="", mode="note"):
        self.db_path = db_path
        self.table_name = table_name
        self.mode = mode

def parse_args(args, conf):
    keys = ["-h", "-d", "-t", "-s", "-i"]
    help = ""
    help += "-h - help\n"
    help += "-d \"db_path.db\" - path to database (required)\n"
    help += "-t \"tabel_name\" - tabel name (required)\n"
    help += "-s <period> - show notes\n"
    help += "\t<period> - period of note showing [all(default), day, last]\n"
    help += "-i - interactive mode\n"

    if "-d" not in args or "-t" not in args:
        print("Error: required specify -d and -t params.\n")
        print(help)
        exit(-1)

    if "-s" in args and "-i" in args:
        print("Error: can not determine the mode. Pleas specify -s or -i.\n")
        print(help)
        exit(-1)

    i = 1
    while i < len(args):
        if args[i] in keys:
            if args[i] == "-h":
                print(help)
                exit(0)
            if args[i] == "-d":
                i += 1
                if i < len(args) and args[i] not in keys:
                    conf.db_path = args[i]
                    i += 1
                    continue
                else:
                    print(f"Error: unexpected value {args[i]} after -d key. Pleas specify path to database after -d.\n")
                    print(help)
                    exit(-1)
            if args[i] == "-t":
                i += 1
                if i < len(args) and args[i] not in keys:
                    conf.table_name = args[i]
                    i += 1
                    continue
                else:
                    print(f"Error: unexpected value {args[i]} after -t key. Pleas specify table name after -t.\n")
                    print(help)
                    exit(-1)
            if args[i] == "-i":
                conf.mode = "interactive"
                i += 1
                continue
            if args[i] == "-s":
                conf.mode = "show"
                conf.period = "all"
                i += 1
                if i < len(args) and args[i] not in keys:
                    if args[i] in ["all", "day", "last"]:
                        conf.period = args[i]
                    else:
                        print(f"Error: unexpected value {args[i]} of period. Pleas specify period after -s.\n")
                        print(help)
                        exit(-1)
                continue
        else:
            print(f"Error: unexpected value {args[i]}.\n")
            print(help)
            exit(-1)


def input_message(msg = ""):
    import os
    os.system(f"echo '{msg}' > /tmp/msg.txt")
    os.system("vim /tmp/msg.txt")
    msg = ""
    if os.path.isfile("/tmp/msg.txt"):
        f = open("/tmp/msg.txt", "r")
        msg = f.read()
        os.remove("/tmp/msg.txt")
        f.close()
    return msg[:-1] if msg and msg[-1] == "\n" else msg


def trim_and_offset(str):
    if len(str) > 100:
        l = str[:101].rfind(" ")
        if l == -1:
            l = 100
        return str[:l] + "\n" + trim_and_offset(" " * 12 + str[l + 1:])
    else:
        return str


def show_notes(notes):
    d = ""
    t = ""
    notes_str = ""
    for note in notes:
        msg, meta = note.message, note.note_meta
        if meta.date != d:
            d = meta.date
            notes_str += d
            notes_str += '\n'
        t_s = "     "
        if t != meta.time[:5]:
            t = meta.time[:5]
            t_s = t
        msg = "\n            ".join([m for m in msg.split("\n") if m])
        notes_str += f"    {t_s} * {msg}"
        notes_str += '\n'
    splited_notes_str = notes_str.split("\n")
    v_msg = ""
    for lstr in splited_notes_str:
        v_msg += trim_and_offset(lstr) + "\n"
    print(v_msg[:-1])


def interactive_show(repository):
    from console_tools.get_key import get_key, KEY
    notes = repository.select_notes()
    notes.reverse()
    current_num = 0
    while True:
        if current_num >= len(notes):
            print("nothing to display")
            break
        print("\n")
        show_notes([notes[current_num]])
        print("[up/down] - ^/v, [edit] - e, [delete] - d, [exit] - esc,q")
        cmd = get_key()
        if cmd == KEY.UP:
            current_num += 1
            if current_num == len(notes):
                current_num = 0
        elif cmd == KEY.DOWN:
            current_num -= 1
            if current_num < 0:
                current_num = len(notes) - 1
        elif cmd == b"E" or cmd == b"e":
            updated_message = input_message(notes[current_num].message)
            notes[current_num].message = updated_message
            repository.update_note(notes[current_num])
        elif cmd == b"D" or cmd == b"d":
            repository.delete_note(notes[current_num])
            notes = repository.select_notes()
            notes.reverse()
        elif cmd == KEY.ESC or cmd == b"q":
            break

def main():
    from datetime import date
    import sys
    conf = Config()

    parse_args(sys.argv, conf)

    repository = Repository(conf.db_path, conf.table_name)

    if conf.mode == "note":
        message = input_message()
        repository.append_note(Note(message))
        show_notes(repository.select_notes(date=date.today().__str__()))

    if conf.mode == "show":
        show_notes(repository.select_notes())

    if conf.mode == "interactive":
        interactive_show(repository)

if __name__ == "__main__":
    main()