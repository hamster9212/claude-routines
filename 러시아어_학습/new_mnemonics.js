// 새로운 연상기억법 데이터 (발음-의미 자연스러운 연결)
// 발음의 음절을 의미와 자연스럽게 연결한 논리적 스토리

const newMnemonics = {
  // === FAMILY (가족) ===
  "кто": {
    meaning: "누가, 누구",
    mnemonic: "크토 → '크~' 의아한 목소리로 '토' 하면서 누가 그래? (의문)",
    story: "누군가를 묻을 때의 의아한 목소리"
  },

  "что": {
    meaning: "무엇이, 무엇",
    mnemonic: "슈토 → '슈~' 뭔가 있는데 '토' 하고 묻는 모습",
    story: "뭔가 있는데 뭐야? 하며 묻는 표정"
  },

  "ма́ма": {
    meaning: "엄마",
    mnemonic: "마-마 → 아기가 엄마를 부르는 소리 '마~마'",
    story: "아기 울음소리와 가장 가까운 단어"
  },

  "па́па": {
    meaning: "아빠",
    mnemonic: "파-파 → 아기가 아빠를 부르는 소리 '파~파'",
    story: "아기가 처음 배우는 두 번째 단어"
  },

  "мать": {
    meaning: "어머니",
    mnemonic: "마-트 → 마더(mother)의 'ma'에 트(정중함)를 더해 '어머니'",
    story: "영어 mother와 발음이 비슷하고, 정중한 표현"
  },

  "оте́ц": {
    meaning: "아버지",
    mnemonic: "오-테-츠 → 오! 테스트(시험)를 통과한 아버지처럼 존경받는 존재",
    story: "아버지는 가족을 지탱하는 존재 (오! 존경)"
  },

  "сын": {
    meaning: "아들",
    mnemonic: "씬 → 씬나게, 기쁘게 뛰어다니는 우리 아들",
    story: "아들은 활발하고 씬나는 존재"
  },

  "дочь": {
    meaning: "딸",
    mnemonic: "도-치 → 도와주는 친절한 딸, 엄마 옆에서 '도' 와주는 존재",
    story: "딸은 엄마 곁에서 항상 도와주는 존재"
  },

  "брат": {
    meaning: "형제, 남자형제",
    mnemonic: "브-랏 → 브라더(brother)의 '브' + 랏(친밀한 느낌)",
    story: "영어 brother와 유사한 발음"
  },

  "сестра́": {
    meaning: "자매, 여자형제",
    mnemonic: "씨-스-뜨-라 → Sister의 'sis' + 뜨(발음) + 라(여성)",
    story: "영어 sister와 비슷한 구조"
  },

  "муж": {
    meaning: "남편",
    mnemonic: "무-쉬 → 무거운 책임을 쉬지 않고 지는 남편",
    story: "남편은 가족의 무거운 책임을 지탱"
  },

  "жена́": {
    meaning: "아내",
    mnemonic: "지-나 → 지나간 시간을 함께한 아내, 평생을 지나며 함께할 존재",
    story: "아내는 평생을 함께하는 가장 가까운 사람"
  },

  "де́душка": {
    meaning: "할아버지",
    mnemonic: "데-두-슈-까 → 데려가고(데), 둘(two)이 함께하는 슈슈(할아버지 소리)",
    story: "할아버지는 손주들을 데려가며 사랑해주는 존재"
  },

  "ба́бушка": {
    meaning: "할머니",
    mnemonic: "바-부-슈-까 → 바-바 하며 손주들을 안는 할머니, 부드러운 포옹",
    story: "할머니의 따뜻한 안아주는 모습"
  },

  "мужчи́на": {
    meaning: "남자",
    mnemonic: "무-쉬-치-나 → 무거운(mu) 책임을 쉬지(shi) 않고 치열하게(chi) 살아가는 나(na)",
    story: "남자는 책임감 있게 삶을 살아가는 존재"
  },

  "же́нщина": {
    meaning: "여자",
    mnemonic: "지-은-시-나 → 지혜(wisdom) 은(silver)처럼 빛나는 여자, 시(시적)인 나",
    story: "여자는 우아하고 지혜로운 존재"
  },

  "студе́нт": {
    meaning: "대학생(남자)",
    mnemonic: "스투-데-은트 → 스튜던트(student) 그 자체, 데고(데이터) 은처럼 배우는 존재",
    story: "영어 student와 거의 같은 발음"
  },

  "студе́нтка": {
    meaning: "대학생(여자)",
    mnemonic: "스투-데-은-까 → 학생 + 카(여성 접미사)",
    story: "스튜던트 + 여성형"
  },

  "учи́тель": {
    meaning: "남자선생님(초중고)",
    mnemonic: "우-치-텔 → 우리를 치유(heal)하고 텔(tell)해주는 선생님",
    story: "선생님은 우리를 가르치고 마음을 터주는 존재"
  },

  "учи́тельница": {
    meaning: "여자선생님(초중고)",
    mnemonic: "우-치-텔-니-짜 → 우치텔(선생님) + 니짜(여성 접미사)",
    story: "남성 교사 + 여성형 접미사"
  },

  "профе́ссор": {
    meaning: "교수",
    mnemonic: "쁘로-페-쏘르 → 프로페셔널(professional) 한 쏘르(sort, 종류)의 선생님",
    story: "영어 professor와 유사한 발음"
  },

  "преподава́тель": {
    meaning: "선생님(대학, 연구소)",
    mnemonic: "쁘레-뽀-다-바-텔 → 준비(prep)해서 뽀대나게 다(전달)하는 바(way)텔(tell)러",
    story: "대학원 수준의 전문적인 강사"
  },

  "ма́льчик": {
    meaning: "남자아이",
    mnemonic: "말-치-크 → 말(horse) 같이 활발하게 뛰는 치열한(chi) 크(크레이지) 아이",
    story: "남자아이는 활발하고 장난꾸러기"
  },

  "де́вочка": {
    meaning: "여자아이",
    mnemonic: "데-보-치-까 → 데빌(devil)처럼 장난꾸러기지만 보(beautiful) 예쁜 아이",
    story: "여자아이는 귀엽고 예쁜 존재"
  },

  "де́вушка": {
    meaning: "아가씨, 젊은 여자",
    mnemonic: "데-부-슈-까 → 데뷔(debut)하는 부드럽고 슈-엘레강트한 아가씨",
    story: "젊은 여성은 새로운 시작과 우아함의 상징"
  },

  "молодо́й челове́к": {
    meaning: "젊은이, 젊은 남자",
    mnemonic: "몰-로-도-이 → 몰려(many) 로또(빛) 도(도전) 아이처럼 젊은 존재",
    story: "젊은이는 희망과 가능성으로 가득한 존재"
  },

  "де́ти": {
    meaning: "아이들",
    mnemonic: "데-띠 → 데데데 (아이들의 재잘거리는 소리) + 띠(tight, 한데 모인)",
    story: "여러 아이들이 함께 있는 모습"
  },

  // === PLACES (장소·시설) ===
  "шко́ла": {
    meaning: "학교(초중고)",
    mnemonic: "슐-라 → 슐~ 랑~ 학교 종 울리는 소리 (쉘(shell) + 라)",
    story: "학교 종을 연상하는 발음"
  },

  "университе́т": {
    meaning: "대학교",
    mnemonic: "우니-베르-씨-떼뜨 → 유니버시티(university) 그 자체",
    story: "영어 university와 거의 같은 발음"
  },

  "институ́т": {
    meaning: "연구소, 대학",
    mnemonic: "인-스띠-뚜-뜨 → 인스티튜션(institution) + 뜨(전문성)",
    story: "영어 institute와 유사한 발음"
  },

  "журна́л": {
    meaning: "잡지",
    mnemonic: "주르-날 → 저널(journal) = 잡지, 그대로의 발음",
    story: "영어 journal 그대로"
  },

  "музе́й": {
    meaning: "박물관",
    mnemonic: "무-제-이 → 뮤지움(museum) 줄여서 뮤즈-이",
    story: "영어 museum을 러시아식으로"
  },

  "кафе́": {
    meaning: "카페",
    mnemonic: "까-페 → 카페 = 커피 마시는 카페 그 자체",
    story: "국제 공용어 그대로"
  },

  "стол": {
    meaning: "탁자, 테이블, 식탁",
    mnemonic: "스-톨 → 스탤(stall) + 톨(tall) = 높이 있는 탁자",
    story: "영어 stall과 유사한 구조"
  },

  "стул": {
    meaning: "의자",
    mnemonic: "스-툴 → 스툴(stool) = 앉는 의자 (작은 탁자 같은)",
    story: "영어 stool과 거의 같은 발음"
  },

  "портфе́ль": {
    meaning: "서류가방",
    mnemonic: "뽀르-뜨-펠 → 포트폴리오(portfolio) 줄인 포르-트펠",
    story: "포트폴리오를 담는 가방"
  },

  "до́ма": {
    meaning: "집에서",
    mnemonic: "도-마 → 도마(집), 마(나) = 나의 집에서",
    story: "집이라는 뜻의 doma"
  },

  "здесь": {
    meaning: "여기",
    mnemonic: "즈-데-스' → 즉(here의 한국식) 데(that) 스(place) = 이곳",
    story: "여기 이 장소를 지칭"
  },

  // === OBJECTS (사물·물건) ===
  "кни́га": {
    meaning: "책",
    mnemonic: "끼-니-가 → 끼니(식사) 때 함께 책을 읽는 느낌",
    story: "책은 식사처럼 정기적으로 읽어야 하는 것"
  },

  "газе́та": {
    meaning: "신문",
    mnemonic: "가-제-따 → 가재(신문처럼 펼쳐짐) 제(zhe) 타(ta) = 펼쳐진 신문",
    story: "신문을 펼치는 모습"
  },

  "письмо́": {
    meaning: "편지",
    mnemonic: "핏-스-모 → 핏(pit, 마음 깊숙이) 스(space) 모(메모) = 마음을 담은 편지",
    story: "마음 깊은 곳에서 나오는 메시지"
  },

  "ру́чка": {
    meaning: "볼펜, 손잡이",
    mnemonic: "루-치-까 → 루(손 lose) 같은 손 + 치(chi, 터치) + 까(catch) = 손잡이",
    story: "손으로 잡는 것, 손과 관련된 물건"
  },

  "слова́рь": {
    meaning: "사전",
    mnemonic: "슬로-바-리 → 슬로우(slow)해도 단어(word) 바(by) 리(list) = 단어 모음",
    story: "느려도 단어를 찾을 수 있는 사전"
  },

  "тетра́дь": {
    meaning: "공책",
    mnemonic: "떼-뜨-라-디 → 떼떼떼 (필기 소리) + 뜨(tight) 라(line) = 줄이 그어진 공책",
    story: "줄 하나하나에 글을 쓰는 공책"
  },

  "ра́дио": {
    meaning: "라디오",
    mnemonic: "라-디-오 → 라디오 = 라디오 그 자체",
    story: "국제 공용어 그대로"
  },

  "пе́сня": {
    meaning: "노래",
    mnemonic: "펜-냐 → 펜(pen)으로 그으면 음악(pe) 냐(나) = 노래가 나온다",
    story: "악보를 그리면 노래가 흘러나온다"
  },

  "му́зыка": {
    meaning: "음악",
    mnemonic: "무-즈-까 → 뮤직(music) = 음악 그 자체",
    story: "영어 music과 거의 같은 발음"
  },

  "каранда́ш": {
    meaning: "연필",
    mnemonic: "까-란-다-시 → 까만(black) 란(랜턴처럼 밝은) 다(다시) 시(시간) = 다시 그릴 수 있는 연필",
    story: "까만 심으로 다시 그릴 수 있는 도구"
  },

  "ле́кция": {
    meaning: "강의",
    mnemonic: "렉-씨-야 → 렉쳐(lecture) 씨(씨앗) 야(night) = 강의를 통한 지식 심기",
    story: "강의는 마음에 지식의 씨앗을 심는 것"
  },

  "вре́мя": {
    meaning: "시간, 시각",
    mnemonic: "브레-미-야 → 브라보(bravo) 미-니 야(야호) = 시간이 지날 때마다 변하는 순간들",
    story: "시간은 순간의 연속"
  },

  "и́мя": {
    meaning: "이름",
    mnemonic: "이-미-야 → 이미(already) 미(me) 야? = 이미 정해진 내 이름",
    story: "태어날 때부터 정해진 내 정체성"
  },

  // === ANIMALS & NATURE (동물·자연) ===
  "живо́тное": {
    meaning: "동물",
    mnemonic: "지-보-톤-노에 → 지금(now) 보(see) 톤(tone) = 살아있고 소리내는 생물",
    story: "살아있는 동물은 움직이고 울음 소리를 낸다"
  },

  "жи́вотный": {
    meaning: "동물의, 생물의",
    mnemonic: "지-보-톤-늬 → 지금 보는 톤의 생명",
    story: "살아있는 것의 특성"
  },

  "ле́с": {
    meaning: "숲",
    mnemonic: "레-스 → 렛(let) + 스(space) = 나뭇잎 자유공간, 울창한 숲",
    story: "숲은 나무들이 자유롭게 자라는 공간"
  },

  "трава́": {
    meaning: "풀",
    mnemonic: "뜨-라-바 → 뜨(tight) 라(line) 바(by) = 빽빽이 자란 풀",
    story: "땅을 촘촘히 덮는 풀"
  },

  "дере́во": {
    meaning: "나무",
    mnemonic: "데-레-보 → 데바(deva, 신) 레(reach) 보(beauty) = 하늘에 닿으려는 아름다운 나무",
    story: "나무는 하늘을 향해 자라려는 생명"
  },

  "цвето́к": {
    meaning: "꽃",
    mnemonic: "쯔-베-톡 → 쯔(color) 베(be) 톡(talk) = 색깔로 말하는 꽃",
    story: "꽃은 아름다운 색깔로 존재를 드러낸다"
  },

  "ли́стья": {
    meaning: "잎, 나뭇잎",
    mnemonic: "리-스-냐 → 리(리듬) 스(swing) 냐 = 바람에 나부끼는 잎",
    story: "바람에 살랑거리며 움직이는 나뭇잎"
  },

  "ко́рень": {
    meaning: "뿌리",
    mnemonic: "코-렌 → 코어(core) 렌(rest) = 나무의 핵심 아래 뿌리",
    story: "나무의 기초가 되는 뿌리"
  },

  "цветно́й": {
    meaning: "색깔의, 칼라의",
    mnemonic: "쯔-벳-노이 → 쯔베(color) 트(trace) = 색깔이 있는",
    story: "색깔이 칠해진 상태"
  },

  "зеленый": {
    meaning: "초록색의",
    mnemonic: "제-레-느-이 → 제로(zero) 레(red) = 빨간색의 반대, 자연색인 초록색",
    story: "자연의 색깔인 초록색"
  },

  "беловый": {
    meaning: "흰색의",
    mnemonic: "베-로-보-이 → 베(be) 로(like) 보(view) = 순수하게 보이는 흰색",
    story: "가장 순수한 색깔"
  },

  "чёрный": {
    meaning: "검은색의",
    mnemonic: "처-르-늬 → 처(char, 검게) 르(rude) = 가장 어두운 색",
    story: "모든 색을 흡수하는 검은색"
  },

  "красный": {
    meaning: "빨간색의",
    mnemonic: "크-라-스-늬 → 크라(cra) 스(shine) = 화려하게 빛나는 빨간색",
    story: "가장 눈에 띄는 색깔"
  },

  "синий": {
    meaning: "파란색의",
    mnemonic: "씨-니-이 → 씨(sea) 니(night) = 바다와 밤의 색 파란색",
    story: "깊고 고요한 느낌의 파란색"
  },

  "жёлтый": {
    meaning: "노란색의",
    mnemonic: "졸-뜨-이 → 졸(zol) 뜨(tight) = 햇빛처럼 따뜻한 노란색",
    story: "햇빛을 연상시키는 노란색"
  },

  "заката": {
    meaning: "석양",
    mnemonic: "자-까-따 → 자(자) 까(깔) 따(땅) = 땅에 깔리는 석양",
    story: "해가 땅으로 깔리며 지는 모습"
  },

  "солнце": {
    meaning: "태양",
    mnemonic: "솔-은-쩨 → 솔(sol, 음악) 은(silver) = 모든 것을 밝혀주는 태양",
    story: "밝고 따뜻한 존재"
  },

  "луна́": {
    meaning: "달",
    mnemonic: "루-나 → 루(lune, 초승달) 나(night) = 밤의 달",
    story: "밤하늘에 떠오르는 달"
  },

  "звезда́": {
    meaning: "별",
    mnemonic: "즈-베-즈다 → 즈(ze) 베(be) = 밤하늘에 반짝이는 별",
    story: "밤하늘의 작은 빛"
  },

  "туча": {
    meaning: "구름",
    mnemonic: "투-차 → 투(two) 차(차르) = 하늘의 큰 덩어리",
    story: "하늘을 덮는 하얀 덩어리"
  },

  "дождь": {
    meaning: "비",
    mnemonic: "도-즈드 → 도(do) 즈드(sud) = 윙윙 쏟아지는 소리",
    story: "빗소리와 함께"
  },

  "снег": {
    meaning: "눈",
    mnemonic: "스-넥 → 스노우(snow) 축약형 + 넥(neck) = 목까지 오는 눈",
    story: "영어 snow와 유사한 발음"
  },

  "вода́": {
    meaning: "물",
    mnemonic: "보-다 → 보(보이다) 다(다른) = 맑게 보이는 액체 물",
    story: "투명하게 보이는 물질"
  },

  "ветер": {
    meaning: "바람",
    mnemonic: "베-뜨-르 → 베(be) 뜨(tight) = 몸에 와닿는 바람",
    story: "피부에 느껴지는 자연의 움직임"
  },

  "воздух": {
    meaning: "공기, 대기",
    mnemonic: "보-즈-두-흐 → 보(void) 즈두(zu) = 빈 공간을 채우는 공기",
    story: "우리가 숨쉬는 보이지 않는 물질"
  },

  "земля́": {
    meaning: "땅, 지구",
    mnemonic: "즘-리야 → 즘(seam) 리(re) 야(ya) = 모든 것이 붙어있는 땅",
    story: "모든 생명이 자라는 기반"
  },

  "гора́": {
    meaning: "산",
    mnemonic: "고-라 → 고(go) 라(라이트) = 높이 올라가야 하는 산",
    story: "하늘을 향해 솟아오른 지형"
  },

  "река́": {
    meaning: "강",
    mnemonic: "레-까 → 렉(wreck) 까 = 계속 흘러가는 강물",
    story: "멈추지 않고 흘러가는 물의 흐름"
  },

  // === ADDITIONAL LESSON 3 WORDS (레슨3 추가 단어) ===
  "дяде́й": {
    meaning: "삼촌, 아저씨",
    mnemonic: "디아-데이 → 디(day) 아(아저씨) = 낮에 자주 보는 아저씨 삼촌",
    story: "친척 남자 어른"
  },

  "тётя": {
    meaning: "아줌마, 숙모",
    mnemonic: "떼-냐 → 떼(team) 냐 = 함께 모여 사는 아줌마",
    story: "친척 여자 어른"
  },

  "невеста": {
    meaning: "신부, 약혼녀",
    mnemonic: "네-베-스-따 → 네(new) 베(be) = 새로 시작하는 신부",
    story: "새로운 삶을 시작하는 여성"
  },

  "жених": {
    meaning: "신랑, 약혼자",
    mnemonic: "지-니-흐 → 지니(genie) 흐 = 모든 소원을 들어줄 신랑",
    story: "신부의 모든 것을 받아줄 신랑"
  },

  "зять": {
    meaning: "사위",
    mnemonic: "지아-뜨 → 지아(ja) 뜨(tight) = 딸을 꼭 안아주는 사위",
    story: "가족에 새로 들어온 남자"
  },

  "невестка": {
    meaning: "며느리",
    mnemonic: "네-베-스-까 → 네(new) 베(be) = 새로 들어온 며느리",
    story: "가족에 새로 들어온 여자"
  },

  "кум": {
    meaning: "대부, 친구",
    mnemonic: "쿰 → 쿰(좋은 친구) = 특별한 친구",
    story: "가장 가까운 친구 같은 존재"
  },

  "кума": {
    meaning: "대모, 친구여자",
    mnemonic: "쿠-마 → 쿰(comb) + 마(mother) = 여자 친구",
    story: "가장 가까운 여자 친구"
  },

  "друг": {
    meaning: "친구",
    mnemonic: "드룩 → 드러(드러내며) 룩(look) = 마음을 드러내는 친구",
    story: "마음을 터놓을 수 있는 존재"
  },

  "подруга": {
    meaning: "여자친구",
    mnemonic: "뽀-드루-가 → 뽀(포) + 드루(드러) = 함께 마음을 터놓는 여자",
    story: "가장 친한 여자 친구"
  },

  "враг": {
    meaning: "적, 원수",
    mnemonic: "브라-크 → 브라(bra, 내 것 지키려) 크(크래쉬) = 싸우는 관계",
    story: "대립 관계에 있는 상대"
  },

  "сосе́д": {
    meaning: "이웃",
    mnemonic: "소-세-드 → 소(so) 세(세) + 드(드넓게) = 옆에 넓게 있는 이웃",
    story: "바로 옆에 사는 사람"
  },

  "сосе́дка": {
    meaning: "여자이웃",
    mnemonic: "소-세-드-까 → 옆 여자 이웃",
    story: "바로 옆에 사는 여자"
  },

  "знако́мый": {
    meaning: "알고 있는 사람, 지인",
    mnemonic: "즈나-코-늬 → 즈(zna) + 코(known) = 알고 있는 사람",
    story: "얼굴을 알고 있는 사람"
  },

  "знако́мая": {
    meaning: "여자 지인",
    mnemonic: "즈나-코-마-야 → 알고 있는 여자",
    story: "알고 지내는 여자"
  },

  "незнако́мый": {
    meaning: "모르는 사람, 낯선 사람",
    mnemonic: "네즈나-코-늬 → 네(not) + 즈나(know) = 모르는 사람",
    story: "처음 보는 낯선 사람"
  },

  "незнако́мая": {
    meaning: "여자 낯선 사람",
    mnemonic: "네즈나-코-마-야 → 모르는 여자",
    story: "처음 보는 여자"
  },

  "люде́й": {
    meaning: "사람(복수),사람들",
    mnemonic: "류-데이 → 류(people) 데이(day) = 하루종일 만나는 사람들",
    story: "여러 사람"
  },

  "люде́й": {
    meaning: "사람들",
    mnemonic: "류-데이 → 루딕(ludic, 사람스러운) = 사람같은",
    story: "집단을 이루는 개인들"
  },

  "челове́к": {
    meaning: "사람, 인간",
    mnemonic: "첼-로-베-크 → 체(che) 로(rogue, 야생) = 문명화된 야생 존재 인간",
    story: "두 발로 선 문명의 존재"
  },

  // === VERBS & ADJECTIVES (동사·형용사) ===
  "есть": {
    meaning: "있다, 먹다",
    mnemonic: "에-스쯔 → 이스(is) + 트(taste) = 있고 먹는 행동",
    story: "소유와 섭취의 이중 의미"
  },

  "быть": {
    meaning: "되다, 있다",
    mnemonic: "비-쯔 → 비(be) + 트(to be) = 존재하는 상태",
    story: "영어 be와 동의의 개념"
  },

  "идти": {
    meaning: "가다, 걷다",
    mnemonic: "이-드-티 → 이동(i-do) 티(tie) = 묶인 신발로 가다",
    story: "신발끈을 묶고 걸어가는 행동"
  },

  "делать": {
    meaning: "하다, 만들다",
    mnemonic: "데-라-뜨 → 데이(day) 라(라이트) = 매일 하는 일",
    story: "매일 반복되는 행동"
  },

  "знать": {
    meaning: "알다, 아는",
    mnemonic: "즈나-뜨 → 즈(zeal) 나(나) = 열정적으로 아는 것",
    story: "깊이 아는 지식"
  },

  "говори́ть": {
    meaning: "말하다, 이야기하다",
    mnemonic: "고-보-릿 → 고(go) 보(voice) = 목소리로 전하는 것",
    story: "입을 열어 전하는 행동"
  },

  "видеть": {
    meaning: "보다, 봤다",
    mnemonic: "비-데-뜨 → 비(be) 데(data) 뜨 = 눈의 데이터로 보다",
    story: "눈으로 확인하는 행동"
  },

  "слы́шать": {
    meaning: "듣다",
    mnemonic: "슬리-샤-뜨 → 슬리(sly) 샤(shatter) = 귀를 쏟아붓는 듣기",
    story: "귀를 활짝 열고 듣는 모습"
  },

  "чита́ть": {
    meaning: "읽다",
    mnemonic: "치-따-뜨 → 치(chi) 따(ta) = 페이지마다 읽어나가는 행동",
    story: "페이지를 넘기며 진행하는 행동"
  },

  "писа́ть": {
    meaning: "쓰다",
    mnemonic: "피-싸-뜨 → 피(pi) 싸(write) = 손으로 쓰는 행동",
    story: "펜으로 글자를 남기는 행동"
  },

  "хоте́ть": {
    meaning: "원하다, 하고 싶다",
    mnemonic: "호-테-뜨 → 호트(hot) = 뜨겁게 원하는 마음",
    story: "열정적으로 바라는 욕구"
  },

  "мо́чь": {
    meaning: "할 수 있다, 가능하다",
    mnemonic: "모-치 → 모(can) + 치(chi) = 능력이 있다",
    story: "신체와 정신의 능력"
  },

  "мога́": {
    meaning: "음.. (능력)",
    mnemonic: "모-까 → 모(모) + 까(까) = 할 수 있는 능력",
    story: "가능성의 표현"
  },

  "мода́": {
    meaning: "유행",
    mnemonic: "모-다 → 모(모) + 다(다) = 지금 유행하는 것",
    story: "시간의 흐름에 따라 변하는 것"
  },

  "прави́ть": {
    meaning: "통치하다, 다스리다",
    mnemonic: "쁘라-빗 → 쁘라(pray) 빗(right) = 올바르게 다스리다",
    story: "옳은 방향으로 이끄는 행동"
  },

  "пра́вда": {
    meaning: "진실, 참",
    mnemonic: "쁘라-즈다 → 쁘라(pray) = 진실을 기도하듯 믿다",
    story: "올바르고 참된 것"
  },

  "пра́вый": {
    meaning: "올바른, 우측의",
    mnemonic: "쁘라-늬 → 쁘라(right) = 정확한 방향",
    story: "옳은 방향"
  },

  "лева́": {
    meaning: "좌측의",
    mnemonic: "레-바 → 레(left) 바(way) = 왼쪽 방향",
    story: "반대쪽 방향"
  },

  "хоро́ший": {
    meaning: "좋은",
    mnemonic: "호-로-시 → 호로(ho로) = 호호하고 웃음이 나오는 좋은 것",
    story: "행복감을 주는 것"
  },

  "плохо́й": {
    meaning: "나쁜",
    mnemonic: "플로-호-이 → 플로(flo) + 호 = 흐름이 나쁜 것",
    story: "흐름을 방해하는 부정적인 것"
  },

  "ста́рый": {
    meaning: "늙은, 오래된",
    mnemonic: "스따-루-이 → 스타(star) 루(rude) = 별처럼 밝아졌던 것이 이제 시들은 것",
    story: "시간이 많이 지난 상태"
  },

  "мла́дый": {
    meaning: "젊은, 어린",
    mnemonic: "믈라-듀-이 → 믈(meld) + 라(라이트) = 아직 밝게 빛나는 젊은 것",
    story: "시작 단계의 밝은 상태"
  },

  "малы́й": {
    meaning: "작은, 적은",
    mnemonic: "말-루-이 → 말(말) 루(루프) = 작은 순환",
    story: "크기가 작은 상태"
  },

  "большо́й": {
    meaning: "큰, 많은",
    mnemonic: "볼-소-이 → 볼(ball) 소(huge) = 큰 공처럼 넓은 것",
    story: "규모가 큰 상태"
  },

  "длинный": {
    meaning: "긴, 오래된",
    mnemonic: "들린-늬 → 들(dll) 린(long) = 길게 늘어난",
    story: "시간이나 거리가 긴 상태"
  },

  "коро́ткий": {
    meaning: "짧은, 가까운",
    mnemonic: "꼬로-키 → 꼬(co) 로(ro) = 돌아서 만나는 근거리",
    story: "길이가 짧거나 거리가 가까운 상태"
  },

  "тёпло": {
    meaning: "따뜻한",
    mnemonic: "떼-뽈로 → 떼(thaw) 뽈로(polo) = 눈이 녹는 따뜻한",
    story: "따뜻함을 주는 온도"
  },

  "холо́дный": {
    meaning: "차가운, 춥다",
    mnemonic: "호-로-드-늬 → 호(hold) + 롤드(cold) = 꼭 잡을 정도로 춥다",
    story: "추위를 느끼는 상태"
  },

  "мо́крый": {
    meaning: "젖은",
    mnemonic: "모-크-루-이 → 모(모) + 크(cream) = 크림처럼 물에 젖은",
    story: "물에 흠뻑 젖은 상태"
  },

  "сухо́й": {
    meaning: "마른, 건조한",
    mnemonic: "수-호-이 → 수(suit) 호(hose) = 호스의 물이 마른 상태",
    story: "수분이 없는 상태"
  },

  "гру́бый": {
    meaning: "거칠은, 무례한",
    mnemonic: "그루-베-이 → 그루(group) 베(베) = 여럿이 모여 드센 것",
    story: "세게 거칠게 표현되는 것"
  },

  "то́нкий": {
    meaning: "얇은, 가느다란",
    mnemonic: "톤-키 → 톤(tone) 키(key) = 섬세한 음색의 얇은 것",
    story: "두께가 얇은 상태"
  },

  "ла́сковый": {
    meaning: "다정한, 애정이 많은",
    mnemonic: "라-스-꼬-베-이 → 라(love) 스(scope) = 깊은 사랑의 범위",
    story: "따뜻한 감정을 표현하는 것"
  },

  "су́ровый": {
    meaning: "가혹한, 엄격한",
    mnemonic: "수-로-베-이 → 수(super) 로(로) = 무지막지하게 혹독한",
    story: "엄하고 차가운 감정"
  },

  "кра́сивый": {
    meaning: "아름다운",
    mnemonic: "크라-씨-비-이 → 크라(color) = 색깔이 아름답게 드러난",
    story: "시각적으로 아름다운 것"
  },

  "безобра́зный": {
    meaning: "못생긴, 추한",
    mnemonic: "베-조-브라-즈-늬 → 베(be) + 조(조) = 조금도 모양이 안 좋은",
    story: "형상이 없고 흉한 상태"
  },

  "о́страя": {
    meaning: "날카로운, 신맛의",
    mnemonic: "오-스-뜨라-야 → 오(오) + 스트라(strangle) = 날카로운 느낌",
    story: "끝이 매운 것"
  },

  "ту́пой": {
    meaning: "둔한, 무딘",
    mnemonic: "투-뽀-이 → 투(two) + 뽀 = 둔한 두 가지 기능",
    story: "날이 무뎌진 상태"
  },

  "бога́тый": {
    meaning: "부유한, 풍부한",
    mnemonic: "보-까-뜨-이 → 보(box) + 까(가득) = 상자가 가득 찬 부자",
    story: "많은 것을 가진 상태"
  },

  "бедный": {
    meaning: "가난한",
    mnemonic: "베-드-늬 → 베(bed) + 드(destitute) = 침대도 없을 정도로 가난한",
    story: "부족함을 느끼는 상태"
  },

  "чи́стый": {
    meaning: "깨끗한, 순수한",
    mnemonic: "치-스-투-이 → 치(clean) + 스투 = 깨끗이 씻은 것",
    story: "불순물이 없는 상태"
  },

  "грязный": {
    meaning: "더러운",
    mnemonic: "그리아-즈-늬 → 그(grit) + 리아(aria) = 모래처럼 더러운",
    story: "쌓여진 먼지와 오물"
  },

  "свеже́е": {
    meaning: "신선한, 최근의",
    mnemonic: "스베-제-이 → 스베(swift) + 제 = 빠르게 신선한 상태",
    story: "최근에 만들어진 상태"
  },

  "черства́я": {
    meaning: "딱딱한, 식은",
    mnemonic: "체르-스바-야 → 체르(char) = 그을린 딱딱한 것",
    story: "오래되어 딱딱해진 상태"
  },

  "светло́й": {
    meaning: "밝은, 밝은색의",
    mnemonic: "스벳-로-이 → 스벳(light) + 로(로) = 빛이 많은",
    story: "밝음이 가득한 상태"
  },

  "мра́чный": {
    meaning: "어두운, 음침한",
    mnemonic: "므라-치-늬 → 므(murk) + 라 = 어두컴컴한 느낌",
    story: "빛이 없는 상태"
  },

  "весёлый": {
    meaning: "즐거운, 유쾌한",
    mnemonic: "베-셀-루-이 → 베(be) + 셀(sell) = 행복감을 파는 느낌",
    story: "기쁨과 웃음이 넘치는 상태"
  },

  "груста́я": {
    meaning: "슬픈, 우울한",
    mnemonic: "그루-스타-야 → 그루(grumble) = 투덜거리는 슬픈 기분",
    story: "마음에 무거움이 있는 상태"
  },

  "спокойны́й": {
    meaning: "침착한, 조용한",
    mnemonic: "스포-코-늬 → 스포(spoke) 코(call) = 차분하게 말하는 것",
    story: "동요하지 않는 평온한 상태"
  },

  "беспокойны́й": {
    meaning: "불안한, 안절부절 못하는",
    mnemonic: "베스-포-코-늬 → 베(be) + 스포 = 침착하지 못한 상태",
    story: "마음이 불안정한 상태"
  },

  "умный": {
    meaning: "똑똑한, 지능의",
    mnemonic: "ум-늬 → 움(hum) = 흐음하며 생각하는 똑똑한 사람",
    story: "지능이 뛰어난 상태"
  },

  "глупый": {
    meaning: "어리석은",
    mnemonic: "글루-뿌-이 → 글루(glue) = 뭔가에 붙어있는 어리석은 상태",
    story: "생각을 하지 못하는 상태"
  },

  "ме́дленный": {
    meaning: "느린",
    mnemonic: "메-드-렌-늬 → 메(med) + 드 = 약을 천천히 마시는 속도",
    story: "시간이 천천히 흐르는 것"
  },

  "быстро́й": {
    meaning: "빠른",
    mnemonic: "비스-뜨로-이 → 비스(piss) + 뜨로 = 빠르게 흘러가는 물처럼",
    story: "빠르게 진행되는 속도"
  },

  "ши́рокий": {
    meaning: "넓은, 광범위한",
    mnemonic: "시-로-키 → 시(sky) + 로 = 하늘처럼 넓은",
    story: "공간이 넓게 펼쳐진 상태"
  },

  "узкий": {
    meaning: "좁은",
    mnemonic: "우즈-키 → 우즈(used) = 많이 다녀 좁아진 길",
    story: "폭이 좁은 상태"
  },

  "высо́кий": {
    meaning: "높은, 큰음량의",
    mnemonic: "비-소-키 → 비(be) + 소(so) = 높이 있는 것",
    story: "위로 솟아오른 상태"
  },

  "ни́зкий": {
    meaning: "낮은",
    mnemonic: "니-즈-키 → 니(ne, not) + 소(so) = 높지 않은",
    story: "아래로 내려온 상태"
  },

  "глубо́кий": {
    meaning: "깊은",
    mnemonic: "글루-보-키 → 글루(glue) + 보 = 깊게 접착된 것",
    story: "밑까지 내려가는 깊이"
  },

  "мелкий": {
    meaning: "얕은, 작은",
    mnemonic: "멜-키 → 멜(melt) = 녹아내린 얕은 깊이",
    story: "깊이가 얕은 상태"
  },

  "тяжело́й": {
    meaning: "무거운",
    mnemonic: "티아-제-로-이 → 티(tie, 결박) + 제(zero) = 결박하는 무거움",
    story: "무게감이 심한 상태"
  },

  "лёгкий": {
    meaning: "가벼운",
    mnemonic: "렉-키 → 렉(leg) = 다리로 가볍게 뛸 수 있는 것",
    story: "무게가 적은 상태"
  },

  "плотны́й": {
    meaning: "조밀한, 두터운",
    mnemonic: "플롯-늬 → 플롯(plot) = 촘촘하게 짜인 계획처럼",
    story: "빈틈없이 채워진 상태"
  },

  "ре́дкий": {
    meaning: "드물은, 희귀한",
    mnemonic: "렛-키 → 렛(let) = 드물게 나타나는 것",
    story: "자주 나타나지 않는 상태"
  },

  "близо́й": {
    meaning: "가까운",
    mnemonic: "블리-소-이 → 블리(bliss) = 행복할 정도로 가까운",
    story: "거리가 가까운 상태"
  },

  "далёкий": {
    meaning: "먼",
    mnemonic: "다-렉-키 → 다(da) + 렉 = 먼 곳까지 갈 거리",
    story: "거리가 먼 상태"
  },

  "горячий": {
    meaning: "뜨거운",
    mnemonic: "고-리아-치 → 고(go) + 리(리아) = 달구어 뜨거운",
    story: "온도가 높은 상태"
  },

  "сладкий": {
    meaning: "달콤한",
    mnemonic: "슬라-드-키 → 슬라(slay) = 마음을 사로잡는 달콤함",
    story: "단맛이 나는 상태"
  },

  "гори́ум": {
    meaning: "쓴(맛의)",
    mnemonic: "고-ри-늬 → 고(go) + 리(leaf) = 잎을 씹은 쓴맛",
    story: "쓴맛이 나는 상태"
  },

  "соля́ный": {
    meaning: "짠",
    mnemonic: "소-렴-늬 → 소(so) + 렴(liaised) = 소금이 섞인",
    story: "짠맛이 나는 상태"
  },

  "кисель": {
    meaning: "신",
    mnemonic: "키-셀 → 키(key) + 셀(sell) = 신 맛의 기본",
    story: "신맛이 나는 상태"
  },

  "мя́сной": {
    meaning: "육류의, 육식의",
    mnemonic: "미아-스노-이 → 미아(meat) = 고기 같은",
    story: "고기로 만든 것"
  },

  "рыбный": {
    meaning: "생선의",
    mnemonic: "리-브-늬 → 리(리) = 강이나 바다의 생선",
    story: "생선으로 만든 것"
  },

  "ма́слений": {
    meaning: "기름진, 기름의",
    mnemonic: "마-슬렌-늬 → 마(ma) + 슬렌(slick) = 기름기로 번지는",
    story: "기름이 많은 상태"
  },

  "сыр": {
    meaning: "치즈",
    mnemonic: "씨르 → 씨(cheese) 랑 비슷한 '씨르'",
    story: "발효된 유제품"
  },

  "мо́локо": {
    meaning: "우유",
    mnemonic: "몰로-꼬 → 몰(mole) + 로 = 영양가 많은 흰 액체",
    story: "소에서 나오는 하얀 액체"
  },

  "хлеб": {
    meaning: "빵",
    mnemonic: "흘렙 → 흘(hull) + 렙(loaf) = 껍질 있는 빵",
    story: "밀가루로 만든 음식"
  },

  "варе́нье": {
    meaning: "잼, 잼 같은 음식",
    mnemonic: "바-렝-예 → 바(boil) + 렝(ring) = 끓여 만든 것",
    story: "열을 가해 만든 음식"
  },

  "коро́вка": {
    meaning: "암소, 소(여)",
    mnemonic: "꼬-로-바-까 → 꼬(cow) = 암소 고유의 울음",
    story: "우유를 주는 동물"
  },

  "буйво́л": {
    meaning: "물소",
    mnemonic: "부-일-볼 → 부(bull) = 물 속의 큰 동물",
    story: "습지에 사는 큰 뿔 동물"
  },

  "свине́й": {
    meaning: "돼지",
    mnemonic: "스비-네-이 → 스비(swine) = 영어 swine 그대로",
    story: "진흙 속에서 사는 동물"
  },

  "ко́за": {
    meaning: "염소",
    mnemonic: "꼬-자 → 꼬(coat) + 자 = 길쭉한 수염 있는 동물",
    story: "수염이 있는 동물"
  },

  "овца́": {
    meaning: "양",
    mnemonic: "오-쯔-아 → 오(oh) + 쯔 = 울음소리 '음메'를 내는 동물",
    story: "털로 가득한 동물"
  },

  "конь": {
    meaning: "말",
    mnemonic: "꼰 → 꼰(con) = 앞다리로 우쭐대는 동물",
    story: "빠르게 달리는 동물"
  },

  "лошадь": {
    meaning: "말(암말)",
    mnemonic: "로-샤-디 → 로(load) = 짐을 운반하는 말",
    story: "짐을 지고 다니는 동물"
  },

  "осёл": {
    meaning: "나귀",
    mnemonic: "오-셀 → 오(oh) + 셀 = 고집스러운 울음의 동물",
    story: "매우 고집스러운 동물"
  },

  "собака́": {
    meaning: "개",
    mnemonic: "소-바-까 → 소(so) + 바(bark) = 멍멍 짖는 반려동물",
    story: "인간과 함께 사는 충성심 있는 동물"
  },

  "кошка": {
    meaning: "고양이",
    mnemonic: "꼬-슈-까 → 꼬(cat) = 고양이 고유의 울음과 모습",
    story: "야옹거리는 우아한 동물"
  },

  "мышь": {
    meaning: "쥐",
    mnemonic: "미-쉬 → 미(mouse) = 쥐의 울음 같은 소리",
    story: "작은 설치류"
  },

  "птица": {
    meaning: "새",
    mnemonic: "쁘띠-자 → 쁘(pretty) + 띠(티) = 예쁜 깃털의 날아다니는 동물",
    story: "하늘을 나는 동물"
  },

  "орёл": {
    meaning: "독수리",
    mnemonic: "오-렬 → 오(oh) = 하늘을 높이 날아다니는 큰 새",
    story: "가장 날카로운 눈의 맹금류"
  },

  "воро́на": {
    meaning: "까마귀",
    mnemonic: "보-로-나 → 보(black) = 검은 색의 까칠한 새",
    story: "검은 깃털의 똑똑한 새"
  },

  "голубь": {
    meaning: "비둘기",
    mnemonic: "고-루-비 → 고(go) + 루(루) = 하늘로 날아다니는 평화로운 새",
    story: "평화의 상징인 새"
  },

  "курица": {
    meaning: "닭(암탉)",
    mnemonic: "쿠-리-자 → 쿠(coo) + 리 = 꼬꼬댁거리는 계집닭",
    story: "계란을 낳는 가금류"
  },

  "петух": {
    meaning: "수탉",
    mnemonic: "쁘-뜨-흐 → 쁘(pretty) = 볏이 자랑스러운 수탉",
    story: "새벽을 알리는 수탉"
  },

  "утка": {
    meaning: "오리",
    mnemonic: "우-까 → 우(water) + 까 = 물에서 헤엄치는 새",
    story: "물에 사는 오리"
  },

  "гусь": {
    meaning: "거위",
    mnemonic: "구-시 → 구(goose) = 거위의 긴 목과 울음",
    story: "길쭉한 목의 수생동물"
  },

  "рыба": {
    meaning: "물고기",
    mnemonic: "리-바 → 리(river) + 바 = 강과 바다의 물고기",
    story: "물에 사는 척추동물"
  },

  "лягу́шка": {
    meaning: "개구리",
    mnemonic: "리아-구-슈-까 → 리(leap) = 뛰어다니는 양서류",
    story: "개굴개굴 우는 동물"
  },

  "змея́": {
    meaning: "뱀",
    mnemonic: "지-미아 → 지(zigzag) = 사이사이로 기어가는 파충류",
    story: "S자로 움직이는 파충류"
  },

  "жи́во": {
    meaning: "살아있게, 생생하게",
    mnemonic: "지-보 → 지(life) + 보(voice) = 살아있는 음성",
    story: "생명력 있는 상태"
  },

  "мёр": {
    meaning: "얼다, 얼었다",
    mnemonic: "멍-뜨 → 멍(minus) = 온도가 마이너스로 떨어져",
    story: "물이 고체로 변하는 과정"
  },

  "при́йти": {
    meaning: "오다, 도착하다",
    mnemonic: "쁘리-이티 → 쁘리(pri) = 앞으로(prior) 걸어오는 것",
    story: "한 곳에서 다른 곳으로 가는 행동"
  },

  "уходи́ть": {
    meaning: "가다, 떠나다",
    mnemonic: "우-호-디-뜨 → 우호(who) = 누가 떠나는 것",
    story: "한 곳에서 나가는 행동"
  },

  "стать": {
    meaning: "되다, 시작하다",
    mnemonic: "스-따-뜨 → 스타(start) = 새로운 상태가 시작된다",
    story: "상태가 변하기 시작하는 순간"
  },

  "гулять": {
    meaning: "산책하다, 놀다",
    mnemonic: "구-렛 → 구(go) + 렛(let) = 자유롭게 다니기",
    story: "야외에서 자유롭게 움직이기"
  },

  "бежа́ть": {
    meaning: "뛰다, 달리다",
    mnemonic: "베-자-뜨 → 베(be) + 자(자신) = 자신의 다리로 뛰다",
    story: "빠르게 움직이는 행동"
  },

  "стоя́ть": {
    meaning: "서 있다",
    mnemonic: "스토-야-뜨 → 스토(stop) = 멈춰서 있는 것",
    story: "한 자리에 서 있는 상태"
  },

  "сиде́ть": {
    meaning: "앉다, 앉아있다",
    mnemonic: "씨-데-뜨 → 씨(sit) = 앉는 행동",
    story: "엉덩이를 의자에 내려놓은 상태"
  },

  "лежа́ть": {
    meaning: "누워있다",
    mnemonic: "레-자-뜨 → 레(lie) + 자 = 누워있는 상태",
    story: "몸을 쭉 펴고 누운 상태"
  },

  "живо́й": {
    meaning: "살아있는, 생생한",
    mnemonic: "지-보-이 → 지(life) + 보(view) = 살아있게 보이는",
    story: "생명력이 있는 것"
  },

  "мёр": {
    meaning: "죽은, 없는",
    mnemonic: "멍-뜨 → 멍(minus) = 생명이 없는 상태",
    story: "생명이 끝난 상태"
  },

  "боя́ть": {
    meaning: "두렵다, 무섭다",
    mnemonic: "보-야-뜨 → 보(bow) = 무서워 인사하는 자세",
    story: "공포감을 느끼는 상태"
  },

  "люби́ть": {
    meaning: "사랑하다, 좋아하다",
    mnemonic: "류-비-뜨 → 류(루) + 비(be) = 그렇게 되기를 원하는 마음",
    story: "깊은 감정적 결합"
  },

  "ненави́деть": {
    meaning: "미워하다, 싫어하다",
    mnemonic: "네-나-비-데-뜨 → 네(not) + 나비(butterfly) = 아름다운 것도 미워하는 극단적 감정",
    story: "상대방을 받아들일 수 없는 감정"
  },

  "ува́жать": {
    meaning: "존경하다, 존중하다",
    mnemonic: "우-바-자-뜨 → 우(u) + 바(way) = 맞는 길로 존경하는 마음",
    story: "상대방의 가치를 인정하는 감정"
  },

  "слуша́ть": {
    meaning: "듣다, 말을 듣다",
    mnemonic: "슬루-샤-뜨 → 슬루(sly) + 샤(shatter) = 조심스럽게 귀를 열고 듣다",
    story: "귀를 기울여 말을 받아들이기"
  },

  "смотре́ть": {
    meaning: "보다, 보고있다",
    mnemonic: "스모-뜨렛 → 스모(small) = 작게라도 보려고 노력하다",
    story: "눈을 뜨고 대상을 관찰하기"
  },

  "кажда́я": {
    meaning: "각각의, 매 ... 마다",
    mnemonic: "까-즈-다-야 → 까(each) + 즈다(that) = 하나하나씩",
    story: "개별적으로 하나씩"
  },

  "все": {
    meaning: "모두, 전부",
    mnemonic: "뷔씨에 → 뷔(view) + 씨에(see) = 모두 보이는",
    story: "전체를 아우르는 것"
  },

  "никто́": {
    meaning: "아무도 아닌, 누구도",
    mnemonic: "닉-토 → 닉(nick) + 토(to) = 아무도 건드릴 것이 없는",
    story: "한 명도 없는 상태"
  },

  "ничто́": {
    meaning: "아무것도 아닌",
    mnemonic: "닉-슈토 → 닉(nick) + 슈토(what) = 아무것도 없는",
    story: "공허한 상태"
  },

  "что́-то": {
    meaning: "뭔가, 어떤 것",
    mnemonic: "슈토-토 → 슈토(what) + 토(to) = 뭔가 있는 것",
    story: "불확정된 어떤 것"
  },

  "кто́-то": {
    meaning: "누군가, 어떤 사람",
    mnemonic: "크토-토 → 크토(who) + 토(to) = 누군가 있는 사람",
    story: "불확정된 어떤 사람"
  },

  "чего́": {
    meaning: "뭘, 뭐의(그 의)",
    mnemonic: "체-고 → 체(what) + 고(go) = 뭔가를 찾아가다",
    story: "무엇을 향한 움직임"
  },

  "кого́": {
    meaning: "누구를",
    mnemonic: "꼬-고 → 꼬(who) + 고(go) = 누구를 찾아가다",
    story: "대상을 지칭하는 표현"
  },

  "мне": {
    meaning: "나에게(여격)",
    mnemonic: "음네 → 음(me) + 네(to) = 나를 향해",
    story: "1인칭 대상 표현"
  },

  "мной": {
    meaning: "나로(인격)",
    mnemonic: "음노이 → 음(me) + 노이(by) = 나를 통해서",
    story: "도구 또는 수단을 나타냄"
  },

  "теб": {
    meaning: "너를(대상)",
    mnemonic: "테-비 → 테(thee) + 비 = 너를 향해",
    story: "2인칭 대상 표현"
  },

  "тобо́й": {
    meaning: "너로(인격)",
    mnemonic: "토-보-이 → 토(to) + 보이 = 너를 통해서",
    story: "도구 또는 수단"
  },

  "себ": {
    meaning: "자신을",
    mnemonic: "세-비 → 세(self) + 비 = 자신을 향해",
    story: "자기 자신을 지칭"
  },

  "собо́й": {
    meaning: "자신으로(인격)",
    mnemonic: "소-보-이 → 소(so) + 보이 = 그렇게 자신을 통해",
    story: "자신을 도구로 쓰는 것"
  },

  "нам": {
    meaning: "우리에게",
    mnemonic: "남 → 남(us) + 에(have) = 우리의 것",
    story: "복수형 대상"
  },

  "вам": {
    meaning: "당신들에게(존댓말)",
    mnemonic: "밤 → 밤(your) = 당신들의 영역",
    story: "존댓말 대상"
  },

  "вас": {
    meaning: "당신을(존댓말 대상)",
    mnemonic: "바-스 → 바(by) + 스 = 당신으로부터",
    story: "존댓말 직접 목적어"
  },

  "вост": {
    meaning: "당신에게(존댓말)",
    mnemonic: "보-시 → 보(to you) + 시 = 당신 쪽으로",
    story: "존댓말 간접 목적어"
  },

  "яму": {
    meaning: "나를(대상1)",
    mnemonic: "야-무 → 야(I) + 무 = 나를 부르다",
    story: "1인칭 직접 목적어"
  },

  "тебя́": {
    meaning: "너를(대상 정식)",
    mnemonic: "테-비아 → 테(thee) + 비아 = 너를 정식으로",
    story: "2인칭 정식 직접 목적어"
  },

  "нас": {
    meaning: "우리를",
    mnemonic: "나-스 → 나(us) + 스 = 우리 전체",
    story: "복수형 직접 목적어"
  },

  "его": {
    meaning: "그를, 그의",
    mnemonic: "이-고 → 이(his) + 고 = 그의 것",
    story: "3인칭 남성 소유격"
  },

  "её": {
    meaning: "그녀를, 그녀의",
    mnemonic: "에-요 → 에(her) + 요 = 그녀의 것",
    story: "3인칭 여성 소유격"
  },

  "их": {
    meaning: "그들을, 그들의",
    mnemonic: "이-흐 → 이(their) + 흐 = 그들의 것",
    story: "3인칭 복수 소유격"
  },

  "мой": {
    meaning: "나의",
    mnemonic: "모-이 → 모(my) + 이 = 내 것",
    story: "1인칭 소유격"
  },

  "твой": {
    meaning: "너의",
    mnemonic: "뜨-보-이 → 뜨(thy) + 보이 = 너의 것",
    story: "2인칭 비존댓말 소유격"
  },

  "наш": {
    meaning: "우리의",
    mnemonic: "나-시 → 나(our) + 시 = 우리 모두의 것",
    story: "1인칭 복수 소유격"
  },

  "ваш": {
    meaning: "당신의(존댓말)",
    mnemonic: "바-시 → 바(your) + 시 = 당신의 것",
    story: "존댓말 소유격"
  },

  "аз": {
    meaning: "나(옛날 러시아식)",
    mnemonic: "아-즈 → 아즈(az) = 옛날 러시아 문자",
    story: "역사적 1인칭"
  }
};

// 데이터 검증
console.log(`총 ${Object.keys(newMnemonics).length}개의 새로운 연상기억법 데이터 생성됨`);
