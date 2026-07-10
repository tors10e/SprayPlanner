def downy_risk(row):
    if row['prcp'] > 2 and 10 <= row['tavg'] <= 25:
        return "HIGH"
    elif row['prcp'] > 0:
        return "MODERATE"
    else:
        return "LOW"


def powdery_risk(row):
    if 21 <= row['tavg'] <= 30:
        return "HIGH"
    elif 15 <= row['tavg'] < 21:
        return "MODERATE"
    else:
        return "LOW"


def botrytis_risk(row):
    if row['prcp'] > 3:
        return "HIGH"
    elif row['prcp'] > 0:
        return "MODERATE"
    else:
        return "LOW"


weather['downy'] = weather.apply(downy_risk, axis=1)
weather['powdery'] = weather.apply(powdery_risk, axis=1)
weather['botrytis'] = weather.apply(botrytis_risk, axis=1)

print(weather[['tavg','prcp','downy','powdery','botrytis']].head(10))


def dominant_disease(row):
    risks = {
        "downy": row['downy'],
        "powdery": row['powdery'],
        "botrytis": row['botrytis']
    }

    if "HIGH" in risks.values():
        return [k for k,v in risks.items() if v == "HIGH"]
    elif "MODERATE" in risks.values():
        return [k for k,v in risks.items() if v == "MODERATE"]
    else:
        return []

