#!/usr/bin/env python
#-*- coding:utf-8 -*-

# simple scripting language & simple interpreter for kids.
# https://github.com/mehmetkose/huhu

# Licensed under the MIT license:
# Copyright (c) 2016 Mehmet Kose mehmetkose122@gmail.com

import sys,os,re

def is_int(s):
    try:
        int(s)
        return True
    except:
        return False
    return False


def _print(command):
    """ değişkeni ekrana yazdırır.
        liste veya string ise yazar,
        yok ise doğrudan değeri yazar.
    """
    if command[0:3] == "yaz":
        key = command.split('yaz')[1].strip()
        value = command.split('yaz')[1].strip()
        if value in globals():
            getval = globals()[key]
            if isinstance(getval, list):
                dump = getval[0]
                for l in getval[1:]:
                    dump = "%s, %s" % (dump, l)
                return 'print("%s")' % dump
            else:
                return 'print("%s")' % getval
        else:
            return 'print("%s")' % value
    else:
        return 'print("%s")' % command


def _set(set_match, line):
    """ değer atama. değişkeşken olarak değer atanabilir
        veya range ile değer üretilip değişkene atanabilir.
    """
    split = line.split('=')
    key = split[0].strip()
    value = split[1].strip()
    range_pattern = '(.*)\.\.(.*)'
    globals()[key] = value

def _range(line):
    """ verilan aralıklarda sayı veya karakter üretir
    """
    # letters = ["a","b","c","ç","d","e","f","g","ğ","h","ı","i","j","k","l","m",
    #             "n","o","ö","p","r","s","ş","t","u","ü","v","y","z"]

    split = line.split('=')
    key = split[0].strip()
    value = split[1].strip()
    range_split = value.split('..')
    to_return = ","
    if is_int(range_split[0]) and is_int(range_split[1]):
        our_list = list(range(int(range_split[0]), int(range_split[1])+1 ))
        new = to_return.join([str(i) for i in our_list])
        return "%s = %s" % (key, new)
    elif isinstance(range_split[0], str) and isinstance(range_split[1], str):
        parse1, parse2 = ord(range_split[0][0]), ord(range_split[1][0])+1
        new = to_return.join([chr(i) for i in list(range(parse1,parse2))])
        return "%s = %s" % (key, new)
    else:
        return "%s = %s" % (key, value)

def _list(list_match, line):
    """ değeri virgülden bölüp liste üretir ve
        değişkene atar.
    """
    split = line.split('=')
    variable = split[0].strip()
    list = [el.strip() for el in split[1].split(",") if el != '']
    globals()[variable] = list


def _for(for_match, line):
    """ atanmış olan listeyi döngüye alır,
        verilen fonkisyonu uygular.
    """
    try:
        getlist = globals()[for_match.group(3).strip()]
        function_name = for_match.group(1).strip()
        function = globals()['_print']
        for i in getlist:
            exec(function(i))
    except:
        return "False"
    return "True"


def _condition(line):
    print("_condition")

def _math(math_pattern, line):
    """ satır içindeki matematik işlemlerini yapar.
    """
    print(re.sub(math_pattern, line,  line))
    # to_replace = str(math_match.string)
    # print(to_replace)
    # return line.replace(to_replace, str(eval(to_replace)))

def _plus(command):
    """ iki ve daha fazla sayıda integer toplanmak üzere gelirse
        ögeler ile klasik toplama işlemi yapılıp geri döndürülür.
        ögelerden biri string ise toplama mantığından çıkılıp
        tüm öğeler string olarak değerlendirilir, birleştirilir
        ve geri döndürülür.
    """
    params = command.replace(' +', '+').replace('+ ', '+').split('+')
    for param in params:
        try:
            param = int(param)
        except:
            pass
    all_integer = True
    for param in params:
        if not isinstance(param, int):
            all_integer = False
    if all_integer:
        to_run = params[0]
        for param in params[1:]:
            to_run = to_run + "+" + param
        return eval(to_run)
    else:
        to_run = params[0]
        for param in params[1:]:
            to_run = to_run + param
        return to_run


def read_line(line):
    # pre_setters
    range_pattern = '(.*)\.\.(.*)'
    math_pattern = '([-+]?[0-9]*\.?[0-9]+[\/\+\-\*])+([-+]?[0-9]*\.?[0-9]+)'
    if re.match(range_pattern, line):
        line = _range(line)
    # if re.match(math_pattern, line):
    #     line = _math(math_pattern, line)
    # after line workers
    list_pattern = '(.*).=.(.*),'
    set_pattern = '(.*).=.(.*)'
    for_pattern = '(.*) (.*) dön (.*)'
    write_pattern = 'yaz (.*)'
    condition_pattern = 'eğer (.*) ise (.*)'
    # bir liste ataması yapılıyor ise
    if re.match(list_pattern, line):
        line = _list(re.match(list_pattern, line), line)
    # değişkene bir str veya int ataması yapılıyor ise
    elif re.match(set_pattern, line):
        line = _set(re.match(set_pattern, line), line)
    # bir döngü mevcut ise
    elif re.match(for_pattern, line):
        line = _for(re.match(for_pattern, line), line)
    # ekrana bir şey yazılıyor ise
    elif re.match(condition_pattern, line):
        line = _condition(line)
    elif re.match(write_pattern, line):
        line = _print(line)
    else:
        line = _print(line)
    return line


def parser(source):
    return [read_line(line) for line in source.split("\n") if line != '']


def main():
    if "huhu" in sys.argv:
        sys.argv.remove('huhu')
    if len(sys.argv[1:]) > 0:
        for i in range(len(sys.argv[1:])):
            if sys.argv[1:][i][0] == "/":
                file_path = sys.argv[1:][i]
            else:
                file_path = "%s/%s" % (os.getcwd(), sys.argv[1:][i])
            if not file_path[-5:] == '.huhu':
                print("dosya uzantısı .huhu olmalıdır")
                break
            try:
                source = open(file_path).read()
            except:
                print("dosyayı bulamadım")
                break
            for result in parser(source):
                if isinstance(result, str):
                    exec(result)
    else:
        print('huhu!')
        while True:
            try:
                command = input('>>> ')
            except:
                print("\n")
                print("güle güle :)")
                return None
            if command.strip() == "çık":
                print("güle güle :)")
                break
            if isinstance(command, str):
                result = read_line(command)
                if result:
                    exec(result)

if __name__ == "__main__":
    main()
