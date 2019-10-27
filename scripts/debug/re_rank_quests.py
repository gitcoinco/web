from quests.models import Quest

for quest in Quest.objects.filter(visible=True):
    pct = quest.success_pct
    ac = quest.attempts.count()
    old_difficulty = quest.difficulty
    if ac > 3:
        if pct > 40:
            quest.difficulty = "Beginner"
        elif pct > 20:
            quest.difficulty = "Intermediate"
        else:
            quest.difficulty = "Advanced"
        quest.save()
        print(pct, "    ", ac, f"                      {old_difficulty} =>  {quest.difficulty}      ", quest.url)
