start = 'ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ'
mid = 'ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ'
end = ' ㄱㄲㄳㄴㄵㄶㄷㄹㄺㄻㄼㄽㄾㄿㅀㅁㅂㅄㅅㅆㅇㅈㅊㅋㅌㅍㅎ'
plus = [start, mid, end]
print(len(start))
print(len(mid))
print(len(end))

a = 8
b = 0
c = 1

value = ((a * 21) + b) * 28 + (c) + 0xAC00
print(chr(value))    # 내 예상엔 '각'이라는 문자가 나와야하는데?