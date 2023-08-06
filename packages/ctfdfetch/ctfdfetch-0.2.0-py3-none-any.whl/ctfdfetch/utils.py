"""Utility functions used to simplify"""

def slugify(name):
    """Utility to create a cleaner printable name (eg: for directories)"""
    return name.replace(' ', '_')


def sort_chals(chals):
    """Sort a challenges list by category and point value"""
    by_cat = {}
    # Group by category
    for c in chals:
        cat = c['category']
        if cat in by_cat:
            by_cat[cat].append(c)
        else:
            by_cat[cat] = [c]

    # sort each category by points
    for cat, cat_list in by_cat.items():
        by_cat[cat] = sorted(by_cat[cat], key=lambda c: int(c['value']))

    # re-create challenge list sorted by category
    res = []
    for cat in sorted(by_cat.keys()):
        res += by_cat[cat]
    return res
