from PoEQuery.official_api_query import StatFilter
from dataclasses import dataclass, fields
from typing import Optional, Tuple
from PoEQuery.stats import stats
from copy import deepcopy


@dataclass(unsafe_hash=True)
class Price:
    type_: str
    amount: float
    currency: str

    def __init__(self, json):
        self.type_, self.amount, self.currency = json["type"], json["amount"], json["currency"]
    
    def __str__(self):
        return f"{self.type_} {self.amount} {self.currency}"

@dataclass(unsafe_hash=True)
class Magnitude:
    hash_: str
    min_: float
    max_: float

    def __init__(self, json):
        self.hash_, self.min_, self.max_ = json["hash"], json["min"], json["max"]
        assert self.hash_ in stats, f"unkown hash {self.hash_}"
        
    def __str__(self):
        #only output the roll string because 
        #can't determin which '#' to substitute without idx in magnitudes list...
        if self.min_ != self.max_:
            roll_string = f"({self.min_}-{self.max_})"
        else:
            roll_string = str(self.min_)
        return roll_string
        


from collections import defaultdict

@dataclass(unsafe_hash=True)
class Mod:
    name: str
    tier: str
    magnitudes: Tuple[Magnitude]

    def __init__(self, json):
        self.name, self.tier = json["name"], json["tier"]
        json_magnitudes = json["magnitudes"] if json["magnitudes"] is not None else []
        self.magnitudes = tuple([Magnitude(magnitude) for magnitude in json_magnitudes])

        self._json = deepcopy(json)

        assert self.name or self.tier or self.magnitudes, f"empty mod: \n {json}"
    
    def to_query_stat_filters(self):
        """
        generates a query stat filter which should represent, to the best possible ability, the mod

        notably, if a stat has multiple entries, we average them to generate the query stat filter
        ie Adds (#1 - #2) to (#3 - #4) Cold Damage becomes min=mean(#1, #2), max=mean(#3, #4) 
        """
        stat_filters = []

        average_found_affix_hashes = defaultdict(list)
        for magnitude in self.magnitudes:
            average_found_affix_hashes[magnitude.hash_].append((magnitude.min_, magnitude.max_))
        
        for hash_, min_max_tuples in average_found_affix_hashes.items():
            mins_, maxs_ = zip(*min_max_tuples)
            min_average = sum(mins_) / len(mins_)
            max_average = sum(maxs_)/len(maxs_)
            min_average, max_average = min(min_average, max_average), max(min_average, max_average)
            stat_filters.append(StatFilter(id=hash_, min=min_average, max=max_average))
        return stat_filters
    
    def to_json(self):
        return deepcopy(self._json)

    def __repr__(self):
        magnitude_strings = []

        hash_to_magnitudes = defaultdict(list)
        for magnitude in self.magnitudes:
            hash_to_magnitudes[magnitude.hash_].append(magnitude)

        for magnitude_hash, magnitude_values in hash_to_magnitudes.items():
            split_stat = stats[magnitude_hash].split("#")

            if len(magnitude_values) == 1 and len(split_stat) == 1:
                # Has some non numeric stat
                magnitude_strings.append("".join(split_stat))
            elif len(split_stat) - 1 == len(magnitude_values):
                #interweave rolls and split str
                rolls = [str(value) for value in magnitude_values]
                final_str = split_stat + rolls
                final_str[::2] = split_stat
                final_str[1::2] = rolls

                magnitude_strings.append("".join(final_str))
            elif len(magnitude_values) ==1 and len(split_stat) > 2:
                rolls = [str(magnitude_values[0])] * (len(split_stat) - 1)
                final_str = split_stat + rolls
                final_str[::2] = split_stat
                final_str[1::2] = rolls
                
                magnitude_strings.append("".join(final_str))
            else:
                raise ValueError(f"wtf Novynn {split_stat}, {magnitude_values}")


        return f"{self.name} {self.tier} {magnitude_strings}"



@dataclass(unsafe_hash=True)
class OfficialApiItem():
    name : str
    type : str
    identified : bool
    ilvl: int
    stack_size : Optional[int] = None
    max_stack_size : Optional[int] = None

    

    def __init__(self, json):
        self.stack_size = json.get("stackSize")
        self.max_stack_size = json.get("maxStackSize")
        self.name = json["name"]
        self.type = json["typeLine"]
        self.identified = bool(json["identified"])
        self.ilvl = json["ilvl"]
        



@dataclass(unsafe_hash=True)
class OfficialApiResult():
    price : Price = None
    implicits : Tuple[Mod] = tuple()
    enchants : Tuple[Mod] = tuple()
    explicits : Tuple[Mod] = tuple()
    fractureds : Tuple[Mod] = tuple()
    crafteds : Tuple[Mod] = tuple()

    def __init__(self,json):

        if "listing" in json and json["listing"]["price"] is not None:
            self.price = Price(json["listing"]["price"])
        else:
            self.price = None
            
        try: 
            self.implicits = tuple([Mod(imp) for imp in json["item"]["extended"]["mods"]["implicit"] if any(imp.values())])
        except KeyError:
            self.implicits = tuple()
            
        try: 
            self.explicits = tuple([Mod(imp) for imp in json["item"]["extended"]["mods"]["explicit"] if any(imp.values())])
        except KeyError:
            self.explicits = tuple() 

        try: 
            self.enchants = tuple([Mod(imp) for imp in json["item"]["extended"]["mods"]["enchant"] if any(imp.values())])
        except KeyError:
            self.enchants = tuple()
        
        try: 
            self.fractureds = tuple([Mod(imp) for imp in json["item"]["extended"]["mods"]["fractured"] if any(imp.values())])
        except KeyError:
            self.fractureds = tuple()

        try: 
            self.crafteds = tuple([Mod(imp) for imp in json["item"]["extended"]["mods"]["crafted"] if any(imp.values())])
        except KeyError:
            self.crafteds = tuple()
        

    def __repr__(self):
        """
        a hacky repr for dataclasses which doesnt display fields which are default values
        """
        arg_strings = []
        for field in fields(self):
            value = getattr(self, field.name)
            if value != field.default:
                arg_strings.append(f"{field.name}={getattr(self, field.name)}")
        
        return f"OfficialApiResult({','.join(arg_strings)})"

