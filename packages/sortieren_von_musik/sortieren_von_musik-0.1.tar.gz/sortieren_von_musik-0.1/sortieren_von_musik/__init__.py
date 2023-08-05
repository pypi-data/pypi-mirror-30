import os, shutil, string
def sort():
    try: ordner = os.listdir("Musik")
    except FileNotFoundError: ordner = []
    for item in ordner:
        a, letter, splitted, album, abc = 1, item.split()[0][0], item.split(" - "), os.listdir(str("Musik/" + item)), list(string.ascii_uppercase) + ["#"]
        for x in range(len(abc)):
            try: os.mkdir(abc[x])
            except FileExistsError: pass
        if letter not in abc: letter = "#"
        try: os.mkdir(letter + "/" + splitted[0]), os.mkdir(letter + "/" + splitted[0] + "/" + splitted[1])
        except (FileExistsError, IndexError) as error: pass
        for x in range(len(album)):
            if ".txt" not in album[x]:
                try: os.mkdir(str(letter + "/") + splitted[0] + "/" + album[x])
                except FileExistsError: pass
        for x in range(len(album)):
            if ".txt" in album[x]: os.rename(str("Musik/" + item + "/" + album[x]), str(letter + "/" + splitted[0] + "/" + splitted[1] + "/" + str(a) + " - " + album[x])); a += 1
            else:
                songs = os.listdir(str("Musik/" + item + "/" + album[x])); a = 1
                for y in range(len(songs)): os.rename(str("Musik/" + item + "/" + album[x]) + "/" + songs[y], str(letter + "/" + splitted[0] + "/" + album[x]) + "/" + str(a) + " - " + songs[y]); a += 1
    try: shutil.move("Musik", "Alt")
    except (FileNotFoundError, FileExistsError, shutil.Error) as error: shutil.rmtree("Musik", ignore_errors=True)
