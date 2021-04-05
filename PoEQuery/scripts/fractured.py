from PoEQuery.official_api import search_and_fetch_batched
from PoEQuery.official_api_query import StatFilters, OfficialApiQuery
from PoEQuery.affix_finder import find_affixes
from tqdm import tqdm

item_classes = dict(
    BOW="weapon.bow",
    CLAW="weapon.claw",
    BASE_DAGGER="weapon.basedagger",
    RUNE_DAGGER="weapon.runedagger",
    ONE_HANDED_AXE="weapon.oneaxe",
    ONE_HANDED_MACE="weapon.onemace",
    ONE_HANDED_SWORD="weapon.onesword",
    SCEPTRE="weapon.sceptre",
    BASE_STAFF="weapon.basestaff",
    WARSTAFF="weapon.warstaff",
    TWO_HANDED_AXE="weapon.twoaxe",
    TWO_HANDED_MACE="weapon.twomace",
    TWO_HANDED_SWORD="weapon.twosword",
    WAND="weapon.wand",
    BODY_ARMOUR="armour.chest",
    BOOTS="armour.boots",
    GLOVES="armour.gloves",
    HELMET="armour.helmet",
    SHIELD="armour.shield",
    QUIVER="armour.quiver",
    AMULET="accessory.amulet",
    BELT="accessory.belt",
    RING="accessory.ring",
    BASE_JEWEL="jewel.base",
    ABYSS_JEWEL="jewel.abyss",
    CLUSTER_JEWEL="jewel.cluster",
)

t = tqdm(item_classes.items())
for item_class_key, item_class_value in t:
    t.set_description(desc=f"item_classes - {item_class_key}")

    mods = find_affixes(
        OfficialApiQuery(
            category=item_class_value,
            corrupted=False,
            fractured=True,
            quality_max=0,
            rarity="nonunique",
        ),
        affix_type="fractured",
    )

    queries = []
    for mod in mods:
        mod_stat_filters = StatFilters(filters=mod.to_query_stat_filters())
        query = OfficialApiQuery(
            category=item_class_value,
            corrupted=False,
            indexed="2week",
            mirrored=False,
            rarity="nonunique",
            stat_filters=[mod_stat_filters],
        )
        queries.append(query)

    results = search_and_fetch_batched(queries)
