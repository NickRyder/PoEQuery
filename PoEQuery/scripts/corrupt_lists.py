from PoEQuery.official_api_query import StatFilter, StatFilters, OfficialApiQuery
from PoEQuery.affix_finder import find_affixes

triple_implicit_stat_filter = StatFilters(filters=[StatFilter(id="explicit.stat_2304729532")],type="not")

item_classes =  dict(
    BOW = "weapon.bow",
    CLAW = "weapon.claw",
    BASE_DAGGER = "weapon.basedagger",
    RUNE_DAGGER = "weapon.runedagger",
    ONE_HANDED_AXE = "weapon.oneaxe",
    ONE_HANDED_MACE = "weapon.onemace",
    ONE_HANDED_SWORD = "weapon.onesword",
    SCEPTRE = "weapon.sceptre",
    BASE_STAFF = "weapon.basestaff",
    WARSTAFF = "weapon.warstaff",
    TWO_HANDED_AXE = "weapon.twoaxe",
    TWO_HANDED_MACE = "weapon.twomace",
    TWO_HANDED_SWORD = "weapon.twosword",
    WAND = "weapon.wand",
    BODY_ARMOUR = "armour.chest",
    BOOTS = "armour.boots",
    GLOVES = "armour.gloves",
    HELMET = "armour.helmet",
    SHIELD = "armour.shield",
    QUIVER = "armour.quiver",
    AMULET = "accessory.amulet",
    BELT = "accessory.belt",
    RING = "accessory.ring",
    BASE_JEWEL = "jewel.base",
    ABYSS_JEWEL = "jewel.abyss",
    CLUSTER_JEWEL = "jewel.cluster")


output_str = ""
for item_class_name, item_class_str in item_classes.items():
    print(item_class_name)
    corrupted_implicits = find_affixes(OfficialApiQuery( category=item_class_str, quality_max=0, rarity="unique", talisman_tier_max=0, synthesised=False, corrupted=True, stat_filters=[triple_implicit_stat_filter]),affix_type="implicit")
    uncorrupted_implicits = find_affixes(OfficialApiQuery( category=item_class_str, quality_max=0, rarity="unique",  talisman_tier_max=0, synthesised=False, corrupted=False),affix_type="implicit")
    output_str += item_class_name + "\n"
    for mod in corrupted_implicits.difference(uncorrupted_implicits):
        output_str += str(mod) + "\n"
 
with open("corrupt_list.txt", "w") as f:
    f.write(output_str) 