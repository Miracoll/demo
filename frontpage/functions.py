from result.models import Result
from configuration.models import Session

def get_top_students():
    # Get second-to-last session safely
    session = Session.objects.order_by('-id')[1]

    # Fetch results for the session
    results = Result.objects.filter(session=session.session,term=4).order_by('group','-average')

    # Process the top 3 students per group
    top_3_per_group = {}
    for result in results:
        group = result.group
        if group not in top_3_per_group:
            top_3_per_group[group] = []
        if len(top_3_per_group[group]) < 3:
            top_3_per_group[group].append(result)

    return top_3_per_group  # Dictionary of top 3 students per group

def get_ordinal_suffix(pos):
    if 10 <= pos % 100 <= 20:  # Covers cases like 11th, 12th, 13th...
        return "th"
    elif pos % 10 == 1:
        return "st"
    elif pos % 10 == 2:
        return "nd"
    elif pos % 10 == 3:
        return "rd"
    else:
        return "th"