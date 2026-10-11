# VistelaCo Instagram Studio (`studio/`)

Інструмент, який робить контент для Instagram VistelaCo: рілси з гачками, каруселі, сторіс і обкладинки хайлайтів. Діана кидає відео або фото в чат або в `studio/inbox/`, ти монтуєш і віддаєш готові файли з `studio/out/`. Усі команди нижче запускай із папки `studio/`. Публікує Діана сама — автопостингу немає.

## Як працювати з Діаною
- Відповідай українською, коротко й чесно. Текст на відео й слайдах — англійською (аудиторія США).
- Факти не вигадуй: ціни, цифри, що є в шаблоні — лише з того, що Діана сказала або що видно у файлі. Прогалини позначай.
- Тексти, гачки й підписи давай блоками коду, щоб їх було легко скопіювати.
- Git: `git fetch origin && git reset --hard origin/main`, нова гілка, один push. Нічого платного не підключай без її «так».
- Репозиторій публічний: фото й відео Діани з `inbox/` і результати з `out/` не комітити (вони в .gitignore). Готові файли віддавай у чат.
- Автоматичну фабрику в корені (build.py, render*.py, queue/, .github/workflows) не чіпай без прямого прохання — це окремий конвеєр, який веде Адріан.

## Структура
- `studio.py` — весь рушій (Pillow + ffmpeg)
- `fonts/` — Playfair Display (+ Italic), Open Sans, Archivo Black (без кирилиці)
- `inbox/` — сюди Діана кладе відео й фото (не в git)
- `out/` — готові файли (не в git)
- `examples/` — зразки JSON для каруселей і сторіс; `examples/ph/` — намальовані замінники фото, не для публікації

Потрібні Python 3, `pip install -r studio/requirements.txt`, ffmpeg. Шрифти вже лежать у `studio/fonts/`.

## Команди
```
python3 studio.py reel inbox/VIDEO.mp4 --hook "..." [--cta DATE] [--mute] [--out out/name.mp4]
python3 studio.py carousel spec.json      # 1080x1350, файли в out/<name>/slide-NN.png
python3 studio.py story spec.json         # 1080x1920, файли в out/<name>/story-NN.png
python3 studio.py phone-video spec.json N inbox/VIDEO.mp4   # слайд N типу phone, відео грає на екрані телефона
python3 studio.py highlights              # 10 обкладинок у out/highlights/
```

## Бренд (каруселі, сторіс, хайлайти, профіль)
- Emerald `#1E4736` — основний; айворі `#FBF8F2` — фон; золото `#C9A867` — лише тонкі лінії, печатка, кікери; чорнило `#0F1F18` — текст.
- Playfair Display — заголовки; Open Sans — текст. Archivo Black — лише латиниця.
- Логотип ще не фінальний: зараз заглушка «курсивна V у тонкому золотому кільці» (`monogram()` у studio.py). Коли буде лого — замінити там.
- Позиціонування: анімовані запрошення на всі свята; весілля — флагман. Обіцянка: розкішний вигляд, який будь-хто робить за кілька хвилин, без дизайнера.

## Рілси — нативний стиль (рішення Діани)
Рілс має виглядати як звичайне відео з Instagram, а не реклама.
- Гачок: білий Open Sans Bold з м'якою тінню, вгорі кадру, перші ~3 с.
- «Comment DATE for the link» тим самим стилем поверх останніх ~2,5 с самого відео.
- НЕ додавати: брендові плашки, зелену фінальну заставку, постійні субтитри внизу.
- Музику скриптом не додати — нагадуй Діані додати трендовий трек в Instagram (у хітах були трендові треки).

Порядок роботи з відео:
1. Витягни 4–6 кадрів (`ffmpeg -ss T -i … -frames:v 1`), подивись їх і коротко опиши, що реально у відео (шаблон, колір, iPad/телефон, тривалість). Не вигадуй того, чого не видно.
2. Запропонуй 3 гачки (мікс груп нижче) — Діана обирає. Якщо каже «роби» — бери найсильніший.
3. Змонтуй, переглянь кадри результату (читабельність на світлому фоні), віддай MP4 + обкладинку `_cover.jpg` + підпис.

### Банк гачків
Група «вже зроблено за вас»:
```
You don't need a designer. Just change the names.
No design skills? This is already made for you
Your guests will open this on their phone
Change the names, hit download, send. That's it.
2027 brides: your save the dates are already designed
Your save the dates, done on your lunch break
```
Група «ціна» (формат хіта на 38 тис. переглядів):
```
Save the date for the price of 2 coffees
I spent under $10 instead of $400 on invitations
$400 on paper invitations? I spent less than $10
My save the dates cost less than my latte order
Paper invites: $400. This: under $10.
Under $10. No printing. No postage.
Your save the dates for less than a pizza
I almost paid $400 for paper. Then I found this.
What $10 gets you instead of $400 of paper
Cheaper than stamps. Prettier than paper.
```
Перед ціновим гачком перевір, що шаблон у ролику справді коштує до $10 (уточни в Діани, якщо невідомо).

### Правила гачків
- Продаємо покупцям, не вчимо: ніколи «how I made», «tutorial», «step by step», не продавати шари/таймлайн/побудову анімації. В Instagram багато людей просять навчити — VistelaCo це не обслуговує.
- Перша особа «я витратила менше $10» — ок. Але ніколи «мої гості», «я розіслала 120», «моє весілля» поверх стокових пар — тільки «your guests».
- Один тригер на всі рілси: DATE.
- Хіти — iPad крупним планом + рука + шаблон у Canva. Стокові пари — максимум 1–2 с «як побачать гості».

### Підпис
Перші два рядки унікальні для кожного рілса, далі стандартний блок Діани. «Link in bio», без тегу @vistelaco, без прямих посилань на лістинги. Приклад:
```
Paper invitations for 100 guests add up fast. This one costs less than two coffees and goes straight to their phones.
Comment DATE and I'll send you the link 💌
```

## Каруселі
JSON-специфікація, слайди типів:
- `cover` — назва + підзаголовок, монограма (theme `light` або `dark`)
- `content` — `kicker` (Tip 1 / Step 2), `title`, `body`
- `photo` — фото на весь слайд, затемнення лише під текстом, `kicker`/`title`/`body`
- `cta` — `title`, `body`, `button` («Comment DATE»)
- `cards` — «стрічка» карток лістингів: два зміщені ряди квадратних фото, що виходять за краї, текст по центру знизу (`images`: 1-й ряд 0–2, 2-й ряд 3–6)
- `phone` — фото продукту на екрані телефона (або `images`: до 3 запрошень стрічкою, центральне — перше) на смарагдовому фоні, під ним `kicker`/`title`/`body` по центру. З `phone-video` — те саме, але на екрані грає відео (Діані так більше подобається, ніж фото на весь слайд).
- Поле `image` у `content` вставляє фото в рамку посередині.

Правила:
- Чергувати фото-слайди й текстові; на обкладинці — продукт у кадрі.
- На фото продукт має бути у верхніх 2/3 — низ іде під текст.
- Корисне = допомога покупцям у плануванні свята: таймлайн розсилки, формулювання (без дітей, без +1, нагадати про RSVP), як надіслати цифрове запрошення, етикет свят. Ніколи — як робити шаблони.
- Пропорція контенту: ~70% продукт (формат iPad), 20% корисне, 10% особисте (смак, вибір кольорів, тренди — не процес створення).

Зразки: `examples/carousel-photo.json`, `carousel-digital.json`, `carousel-wording.json`.

## Сторіс
Ті самі типи слайдів, 9:16. Скрипт сам піднімає текст над нижніми ~25% (там інтерфейс Instagram і місце під стікер-посилання) і прибирає футер. Стікери, опитування, посилання Діана ставить в Instagram.
Зразки: `examples/story-photo.json`, `story-example.json`.

## Хайлайти
Порядок: Shop, Halloween (до 31.10, потім в архів), Christmas (до кінця грудня), Save the Date, Birthday, Websites, Reviews, How it works, FAQ, Hi I'm Diana. Сезонне свято завжди стоїть одразу після Shop. У кожному — сторіс зі стікером на відповідну секцію Etsy (посилання дає Діана). Reviews — скріни відгуків з Etsy (їх уже понад 10).
Сторіс для хайлайтів: `examples/story-shop.json`, `story-christmas.json`, `story-halloween.json`, `story-example.json` (How it works). Найкраще між ними — реальне відео шаблону.
FAQ — найчастіші питання покупців: де шаблон, як зробити QR, як працює RSVP, як опублікувати сайт, куди надіслати відео.

## Профіль (рекомендації, ще не впроваджені)
- Handle @vistelaco, ім'я «Diana · VistelaCo» (зараз dianacreativedesign.co).
- Закріпити три хіти (76 тис., 38 тис., 13,6 тис.).
- Біо на кшталт: «Animated wedding invitations · edit in free Canva in minutes · no design skills needed».

## Перед здачею
Завжди переглядай кадри/слайди результату перед тим, як віддати. Якщо текст погано читається на конкретному фото — підкоригуй, а не віддавай як є.
