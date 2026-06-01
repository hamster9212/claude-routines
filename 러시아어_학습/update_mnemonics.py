#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import json

# 새로운 연상기억법 데이터 (위의 JavaScript 데이터를 Python 딕셔너리로 변환)
new_mnemonics = {
    "кто": "크토 → '크~' 의아한 목소리로 '토' 하면서 누가 그래? (의문)",
    "что": "슈토 → '슈~' 뭔가 있는데 '토' 하고 묻는 모습",
    "ма́ма": "마-마 → 아기가 엄마를 부르는 소리 '마~마'",
    "па́па": "파-파 → 아기가 아빠를 부르는 소리 '파~파'",
    "мать": "마-트 → 마더(mother)의 'ma'에 트(정중함)를 더해 '어머니'",
    "оте́ц": "오-테-츠 → 오! 테스트(시험)를 통과한 아버지처럼 존경받는 존재",
    "сын": "씬 → 씬나게, 기쁘게 뛰어다니는 우리 아들",
    "дочь": "도-치 → 도와주는 친절한 딸, 엄마 옆에서 '도' 와주는 존재",
    "брат": "브-랏 → 브라더(brother)의 '브' + 랏(친밀한 느낌)",
    "сестра́": "씨-스-뜨-라 → Sister의 'sis' + 뜨(발음) + 라(여성)",
    "муж": "무-쉬 → 무거운 책임을 쉬지 않고 지는 남편",
    "жена́": "지-나 → 지나간 시간을 함께한 아내, 평생을 지나며 함께할 존재",
    "де́душка": "데-두-슈-까 → 데려가고(데), 둘(two)이 함께하는 슈슈(할아버지 소리)",
    "ба́бушка": "바-부-슈-까 → 바-바 하며 손주들을 안는 할머니, 부드러운 포옹",
    "мужчи́на": "무-쉬-치-나 → 무거운(mu) 책임을 쉬지(shi) 않고 치열하게(chi) 살아가는 나(na)",
    "же́нщина": "지-은-시-나 → 지혜(wisdom) 은(silver)처럼 빛나는 여자, 시(시적)인 나",
    "студе́нт": "스투-데-은트 → 스튜던트(student) 그 자체, 데고(데이터) 은처럼 배우는 존재",
    "студе́нтка": "스투-데-은-까 → 학생 + 카(여성 접미사)",
    "учи́тель": "우-치-텔 → 우리를 치유(heal)하고 텔(tell)해주는 선생님",
    "учи́тельница": "우-치-텔-니-짜 → 우치텔(선생님) + 니짜(여성 접미사)",
    "профе́ссор": "쁘로-페-쏘르 → 프로페셔널(professional) 한 쏘르(sort, 종류)의 선생님",
    "преподава́тель": "쁘레-뽀-다-바-텔 → 준비(prep)해서 뽀대나게 다(전달)하는 바(way)텔(tell)러",
    "ма́льчик": "말-치-크 → 말(horse) 같이 활발하게 뛰는 치열한(chi) 크(크레이지) 아이",
    "де́вочка": "데-보-치-까 → 데빌(devil)처럼 장난꾸러기지만 보(beautiful) 예쁜 아이",
    "де́вушка": "데-부-슈-까 → 데뷔(debut)하는 부드럽고 슈-엘레강트한 아가씨",
    "молодо́й челове́к": "몰-로-도-이 → 몰려(many) 로또(빛) 도(도전) 아이처럼 젊은 존재",
    "де́ти": "데-띠 → 데데데 (아이들의 재잘거리는 소리) + 띠(tight, 한데 모인)",
    "шко́ла": "슐-라 → 슐~ 랑~ 학교 종 울리는 소리 (쉘(shell) + 라)",
    "университе́т": "우니-베르-씨-떼뜨 → 유니버시티(university) 그 자체",
    "институ́т": "인-스띠-뚜-뜨 → 인스티튜션(institution) + 뜨(전문성)",
    "журна́л": "주르-날 → 저널(journal) = 잡지, 그대로의 발음",
    "музе́й": "무-제-이 → 뮤지움(museum) 줄여서 뮤즈-이",
    "кафе́": "까-페 → 카페 = 커피 마시는 카페 그 자체",
    "стол": "스-톨 → 스탤(stall) + 톨(tall) = 높이 있는 탁자",
    "стул": "스-툴 → 스툴(stool) = 앉는 의자 (작은 탁자 같은)",
    "портфе́ль": "뽀르-뜨-펠 → 포트폴리오(portfolio) 줄인 포르-트펠",
    "до́ма": "도-마 → 도마(집), 마(나) = 나의 집에서",
    "здесь": "즈-데-스' → 즉(here의 한국식) 데(that) 스(place) = 이곳",
    "кни́га": "끼-니-가 → 끼니(식사) 때 함께 책을 읽는 느낌",
    "газе́та": "가-제-따 → 가재(신문처럼 펼쳐짐) 제(zhe) 타(ta) = 펼쳐진 신문",
    "письмо́": "핏-스-모 → 핏(pit, 마음 깊숙이) 스(space) 모(메모) = 마음을 담은 편지",
    "ру́чка": "루-치-까 → 루(손 lose) 같은 손 + 치(chi, 터치) + 까(catch) = 손잡이",
    "слова́рь": "슬로-바-리 → 슬로우(slow)해도 단어(word) 바(by) 리(list) = 단어 모음",
    "тетра́дь": "떼-뜨-라-디 → 떼떼떼 (필기 소리) + 뜨(tight) 라(line) = 줄이 그어진 공책",
    "ра́дио": "라-디-오 → 라디오 = 라디오 그 자체",
    "пе́сня": "펜-냐 → 펜(pen)으로 그으면 음악(pe) 냐(나) = 노래가 나온다",
    "му́зыка": "무-즈-까 → 뮤직(music) = 음악 그 자체",
    "каранда́ш": "까-란-다-시 → 까만(black) 란(랜턴처럼 밝은) 다(다시) 시(시간) = 다시 그릴 수 있는 연필",
    "ле́кция": "렉-씨-야 → 렉쳐(lecture) 씨(씨앗) 야(night) = 강의를 통한 지식 심기",
    "вре́мя": "브레-미-야 → 브라보(bravo) 미-니 야(야호) = 시간이 지날 때마다 변하는 순간들",
    "и́мя": "이-미-야 → 이미(already) 미(me) 야? = 이미 정해진 내 이름",
}

# HTML 파일 읽기
with open('index.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

# 연상기억법 섹션 찾기
mnemonic_start = html_content.find('<section id="sec-mnemonic"')
mnemonic_end = html_content.find('</section>', mnemonic_start) + len('</section>')

if mnemonic_start == -1:
    print("ERROR: mnemonic section not found!")
    exit(1)

old_mnemonic_section = html_content[mnemonic_start:mnemonic_end]

# 모든 <tr>태그에서 러시아어 단어 추출
pattern = r'<tr><td class="ru">([^<]+)</td><td>([^<]+)</td><td>([^<]+)</td></tr>'
rows = list(re.finditer(pattern, old_mnemonic_section))

print(f"Found {len(rows)} mnemonic rows in the original section")

# 업데이트할 행 수 카운트
updated_count = 0
for match in rows:
    russian = match.group(1)
    if russian in new_mnemonics:
        updated_count += 1

print(f"Will update {updated_count} rows with new mnemonics")

# 업데이트된 섹션 생성
new_mnemonic_section = old_mnemonic_section
for russian, old_mnemonic in re.findall(pattern, old_mnemonic_section):
    if russian in new_mnemonics:
        # 찾아서 교체
        old_row = f'<tr><td class="ru">{russian}</td><td>{re.search(f"<tr><td class=\"ru\">{re.escape(russian)}</td><td>([^<]+)</td>", old_mnemonic_section).group(1)}</td><td>{re.search(f"<tr><td class=\"ru\">{re.escape(russian)}</td><td>[^<]+</td><td>([^<]+)</td></tr>", old_mnemonic_section).group(1)}</td></tr>'
        new_row = f'<tr><td class="ru">{russian}</td><td>{re.search(f"<tr><td class=\"ru\">{re.escape(russian)}</td><td>([^<]+)</td>", old_mnemonic_section).group(1)}</td><td>{new_mnemonics[russian]}</td></tr>'
        new_mnemonic_section = new_mnemonic_section.replace(old_row, new_row, 1)

# 전체 HTML 업데이트
new_html_content = html_content[:mnemonic_start] + new_mnemonic_section + html_content[mnemonic_end:]

# 저장
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(new_html_content)

print(f"Successfully updated index.html!")
print(f"Total {updated_count} mnemonics updated")

