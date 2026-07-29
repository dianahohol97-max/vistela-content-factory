# Veo / Gemini — промпти для інтро-сцен (wedding couples)

Це стартові хук-сцени для рілсів (idуть перед phone-reveal). Формат: **9:16, 5–8 секунд**.
Пайплайн сам обріже до 3.5 с, тож головна емоція має бути з першої секунди.
Кладеш готові у Dropbox `/весільні відео` — далі все автоматично.

---

## База стилю (додавай перед кожним промптом)

> Vertical 9:16 cinematic video, shot on 35mm film look, soft natural light,
> shallow depth of field, warm romantic color grading, elegant wedding editorial
> style, smooth slow motion, no text, no logos, no watermarks.

## Правила

- **Перша секунда = емоція.** Рух має вже відбуватись на старті (не «розгойдування»).
- Обличчя можуть бути видимі або відвернені — обидва варіанти працюють; зі спини
  часто виглядає дорожче і безпечніше по якості генерації.
- Проси **very slow, subtle camera movement** — швидкі панорами ламаються.
- Під кожен продуктовий колір є своя сцена (dusty blue → берег/сутінки,
  emerald → сад/зелень, blush → золота година).

---

## 12 сцен

1. **Нічна прогулянка** (пасує до будь-чого)
   > Bride and groom walking away from camera down a city street at night, her
   > long white dress flowing, he holds her hand, warm streetlights bokeh,
   > candid laughing moment, handheld documentary feel.

2. **First look — він обертається**
   > Groom in a navy suit turns around to see the bride for the first time in a
   > garden, genuine emotional reaction, she smiles in a lace dress holding a
   > bouquet of white and dusty blue flowers.

3. **Фата на вітрі** (dusty blue)
   > Close-up of a bride's veil catching the sea breeze on a cliffside at dusk,
   > soft blue hour light, she laughs and holds the veil, ocean blurred behind.

4. **Біг по пляжу**
   > Bride and groom running barefoot along the shoreline at golden hour holding
   > hands, dress and veil flying, joyful, camera tracking alongside them.

5. **Танець на терасі** (emerald / garden)
   > Couple slow-dancing on a stone terrace surrounded by lush green ivy and
   > string lights at twilight, she rests her head on his shoulder, fairy-light bokeh.

6. **Руки та обручки**
   > Extreme close-up of a groom sliding a ring onto the bride's hand, her
   > delicate manicure, his hands trembling slightly, soft window light, linen suit.

7. **Келихи й сміх** (весела енергія)
   > Bride and groom clinking champagne glasses and laughing at a candlelit
   > dinner table with white flowers, golden sparkle bokeh, candid joy.

8. **Кружляння** (universal hero)
   > Groom lifts and spins the bride in a sunlit meadow, her dress twirling,
   > genuine laughter, lens flare through the trees, camera slowly circling them.

9. **Під дощем** (драматично-романтичне)
   > Couple kissing under a clear umbrella in soft rain on an old European
   > street at dusk, warm lantern light, rain drops sparkling in slow motion.

10. **Ранок нареченої** (getting ready)
    > Bridesmaids in matching dusty blue silk robes helping the bride with the
    > last button of her dress, morning window light, champagne glasses nearby,
    > soft laughter.

11. **Конфеті / пелюстки**
    > Bride and groom walking down ceremony aisle as guests throw white flower
    > petals, both laughing, petals falling in slow motion, seaside arch behind.

12. **Тихий момент — чоло до чола**
    > Bride and groom standing forehead to forehead with closed eyes at sunset
    > on a hilltop, wind moving her hair and veil gently, intimate and calm,
    > silhouette rim light.

---

## Бонус: сцени під конкретні палітри

- **Dusty Blue:** додай до будь-якої сцени → "dusty blue color accents: bridesmaid
  dresses, ribbon details and florals in muted slate blue tones"
- **Emerald:** → "deep emerald green accents: velvet decor, foliage, groom's tie"
- **Blush / Dusty Rose:** → "blush pink accents: rose petals, soft pink florals,
  warm golden hour glow"
- **Champagne Gold:** → "champagne and gold accents: sequin details, candlelight,
  warm amber tones"

## Технічне

- Генеруй 2–3 дублі на сцену і бери найкращий — руки/обличчя інколи пливуть.
- Файли назви як зручно — пайплайн сам їх підхопить з `/весільні відео`
  (ротація стежить, щоб сцена × продукт не повторювались).
- Звук з генерації не потрібен — рілси йдуть зі своєю музикою.
