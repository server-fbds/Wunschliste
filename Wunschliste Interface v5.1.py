import os
import random
import base64
import time
os.system('cls' if os.name == 'nt' else 'clear')

_version = 5.1

names = [
  'Sebastian',
  'Bettina',
  'Nora',
  'Anna',
  'Finn'
]

styles = {
  'cyan'   : '\033[96m',
  'green'  : '\033[92m',
  'red'    : '\033[91m',
  'bold'   : '\033[1m',
  'normal' : '\033[0m',
  'cursive': '\033[3m'
}

def main():
  global styles, names
  os.chdir(os.path.realpath(__file__)[:-(len(os.path.basename(__file__)))])
  change_cwd()
  if check_updates():
    return

  user = input('Gib deinen Namen ein: ').title()
  if user not in names:
    print(f'{styles["red"]}{user} ist kein gültiger Name!{styles["normal"]}')
    return main()
  
  wünsche = get_wishes(user)
  print_wishes(user, correct_wishes(wünsche, owner=True))
  input('\nEnter um fortzufahren...')
  
  menu(user)

def menu(user,*, _input=None):
  global names, styles
  clear()

  if _input is None:
    printf('Drücke: \n' +
           '"e" um die eigenen Wünsche zu sehen\n' +
           '"m" um deine Geschenke an andere zu sehen\n' +
           '"a" um die Wünsche von den anderen zu sehen\n' +
           '"r" um deine Wünsche und Geschenke zurückzusetzten (Nur benutzten wenn das Geschenkevent vorbei ist!)\n' +
           '"q" um das Programm zu beenden\n', style='green')
    _input = input().lower()[0]

  match _input:
    case 'e':
      clear()

      wünsche = get_wishes(user)
      print_wishes(user, correct_wishes(wünsche, owner=True))

      add_wish(user)
      return
    case 'a':
      clear()
      others = names.copy()
      others.remove(user)
      start = 1
      alle_wünsche = []
      raw_wishes = []
      for i, other in enumerate(others):
        wünsche = correct_wishes((raw_wish := get_wishes(other)))
        raw_wishes.append(raw_wish)
        alle_wünsche.append(wünsche)
        if wünsche:
          start = print_wishes(other, wünsche, start) + 1
      
      if not (versuch := input('Wenn du einen Wunsch erfüllen willst, gib die Zahl ein. Ansonsten Enter um zurückzukehren... ')):
        return menu(user)
      
      try:
        wunsch_index = int(versuch) - 1
      except:
        printf('Fehler! Veruchs noch einmal!', style='red')
        time.sleep(1)
        return menu(user, _input = 'a')
      while alle_wünsche:
        if wunsch_index >= (length := len(alle_wünsche[0])):
          wunsch_index -= length
          alle_wünsche.pop(0)
          raw_wishes.pop(0)
          others.pop(0)
          others
          continue
        wunsch = (neue_wünsche := alle_wünsche[0])[wunsch_index]
        other = others[0]
        printf(f'Bist du dir sicher, dass du {other} den Wunsch {wunsch} erfüllen willst? ', style='red')
        if input().lower() in ('ja', 'j'):
          if check_changes(other, raw_wishes[0]):
            neue_wünsche[wunsch_index] = '#' + wunsch
            if update(other, neue_wünsche):
              add_geschenk(user, other, wunsch)
              printf('Erfolgreich', style='green')
              time.sleep(1)
              return menu(user, _input = 'a')
          else:
            printf('Fehler! Versuchs noch einmal!', style='red')
            time.sleep(1)
            return menu(user, _input = 'a')
        else:
          printf('Kehre zurück!', style='green')
          time.sleep(1)
          return menu(user)
      printf('Zu hoher Wert! Versuches noch einmal!')
      time.sleep(1)
      return menu(user, _input = 'a')
        
    case 'q':
      return
    case 'm':
      clear()
      geschenke = get_geschenke(user)
      print_geschenke(user, geschenke)
      input('Enter um fortzufahren... ')
      return menu(user)
    case 'r':
      printf('Bist du dir sicher, dass du deine Geschenke und Wünsche zurücksetzten willst? ', style='red')
      if input().lower() in ('ja', 'j', 'yes'):
        reset(user)
        printf('Erfolgreich!', style='green')
        time.sleep(1)
      return menu(user)

    case other:
      print(f'{other} is not valid')
      time.sleep(1)
      return menu(user)


def clear():
  os.system('cls' if os.name == 'nt' else 'clear')

def update(name, wünsche) -> bool:
  with open('Wünsche/' + name, 'w') as file:
    file.write(name)
    for wunsch in wünsche:
      file.write('\n' + encode(wunsch))
  return True

def check_changes(user, wünsche):
  return get_wishes(user) == wünsche

def encode(text):
  seed = random.randint(268435456, 4294967295)
  random.seed(seed)
  bytes = bytearray(text.encode('utf-8'))
  for i in range(len(bytes)):
    if random.random() < 0.5:
      bytes[i] ^= (1 << random.randint(0, 7))
  encoded_bytes = base64.b64encode(bytes)
  return encoded_bytes.decode('utf-8') +  str(hex(seed))

def decode(encoded_text):
  seed = int(encoded_text[-10:], base=16)
  random.seed(seed)
  encoded_text = encoded_text[:-10]
  decoded_bytes = base64.b64decode(encoded_text)
  modified_bytes = bytearray(decoded_bytes)
  for i in range(len(modified_bytes)):
    if random.random() < 0.5:
      modified_bytes[i] ^= (1 << random.randint(0, 7))
  return modified_bytes.decode('utf-8')

def get_wishes(name) -> list[str]:
  with open('Wünsche/' + name, 'r') as file:
    name, *wünsche = file.read().splitlines()
  decoded_wünsche = list(map(decode, wünsche))
  return decoded_wünsche

def get_geschenke(name) -> dict[str:list[str]]:
  geschenke_dict = {name : [] for name in names}
  with open('Geschenke/' + name, 'r') as file:
    name, *geschenktes = file.read().splitlines()
  decoded_geschenktes = list(map(decode, geschenktes))
  for geschenktes in decoded_geschenktes:
    name2, geschenk = geschenktes.split('ç')
    geschenke_dict[name2].append(geschenk)
  return geschenke_dict

def add_wish(name) -> None:
  wunsch = input("Was wünschst du dir noch? (Nichts eigeben um zurückzugehen) ").title().strip()
  if not wunsch:
    print('Erfolgleich abgebrochen!')
    time.sleep(1)
    return menu(name)
  keep = input('Nur einmal? ').lower().strip() in ('n', 'nein', 'nö')
  if input(f'{styles["red"]}Bist du dir sicher, dass du dir {wunsch + (" (Mehrmals)" if keep else "")} wünschst? {styles["normal"]}') not in ('ja', 'j', 'yes'):
    print('Erfolgleich abgebrochen!')
    time.sleep(1)
    return
  with open('Wünsche/' + name, 'a') as file:
    file.write('\n' + encode(wunsch + (' (Mehrmals)' if keep else '')))
  return menu(name, _input = 'e')

def add_geschenk(self, other, geschenk):
  with open('Geschenke/' + self, 'a') as file:
    file.write('\n' + encode(f'{other}ç{geschenk}'))

def change_cwd() -> None:
  if not os.path.isfile("helper"):
    path = input("Copy paste den Pfad zum Wunschlistenordner hier hin: ")
    with open('helper', 'w') as file:
      file.write(path)
  else:
    with open('helper', 'r') as file:
      path = file.read()
  os.chdir(path)

def correct_wishes(wünsche, owner=False) -> list[str]:
  if owner:
    return [wunsch[1:] if wunsch[0] == '#' else wunsch for wunsch in wünsche]
  else:
    return [wunsch for wunsch in wünsche if wunsch[0] != '#']

def print_wishes(user, wünsche, start = 1) -> None:
  i = start
  print(f'{user} Wünscht sich:{styles["cyan"]}\n')
  for i, wunsch in enumerate(wünsche, start):
    print(i, wunsch)
  print(styles['normal'])
  return i

def print_geschenke(user, dict_geschenke:dict):
  for name, geschenke in dict_geschenke.items():
    if not geschenke or user == name:
      continue

    print(f'\nDu schenkst {name}:{styles["cyan"]}\n')
    if not geschenke:
      print('Nichts')
    for geschenk in geschenke:
      print(geschenk)
    print(styles["normal"])

def reset(user):
  with open('Wünsche/' + user, 'w') as file:
    file.write(user)
  with open('Geschenke/' + user, 'w') as file:
    file.write(user)

def printf(text, *,style='normal'):
  print(styles[style] + text + styles['normal'])

def check_updates() -> bool:
  global _version
  
  possible_updates = [_version + i + (round(j/10, 1) if j else 0) for i in range(5) for j in range(5)]
  possible_updates.sort(reverse=True)
  possible_updates.pop()

  for poss in possible_updates:
    if os.path.isfile(os.path.join('Versionen', f'Wunschliste Interface v{poss}.py')):
      printf(f'Update erkannt! Möchtest du zu Version {poss} upgraden?', style='cyan')
      if input().lower() in ('ja', 'j'):
        update_version(poss)
        print('Erfolgreich! Starte das Programm neu!')
        time.sleep(2)
        return True
      return False

def update_version(version):
  with open(os.path.join('Versionen', f'Wunschliste Interface v{version}.py'), 'r') as new_file:
    code = new_file.read()
  with open(__file__, 'w') as current_file:
    current_file.write(code)
  if (filename := os.path.basename(__file__)) == f'Wunschliste Interface v{_version}.py':
    os.rename(__file__, os.path.join(os.path.realpath(__file__)[:-(len(os.path.basename(__file__)))], f'Wunschliste Interface v{version}.py'))

if __name__ == '__main__':
  main()