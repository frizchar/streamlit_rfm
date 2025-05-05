# arguments (x = value, p = recency, k = quartiles dict)
def RClass(x, p, d):
    if x <= d[p][0.25]:
        return 1
    elif x <= d[p][0.50]:
        return 2
    elif x <= d[p][0.75]:
        return 3
    else:
        return 4


# arguments (x = value, p = monetary_value OR frequency, k = quartiles dict)
def FMClass(x, p, d):
    if x <= d[p][0.25]:
        return 4
    elif x <= d[p][0.50]:
        return 3
    elif x <= d[p][0.75]:
        return 2
    else:
        return 1


# define mapping logic for profiles
def rfm_segment(rfm_code):
    # Extract R, F, M as integers
    r, f, m = map(int, list(rfm_code))

    # Define rules based on common RFM segmentation logic
    if r == 1 and f == 1 and m == 1:
        return 'champion'
    elif r == 1 and f <= 2 and m <= 2:
        return 'loyal_customer'
    elif r <= 2 and f <= 3 and m <= 3:
        return 'potential_loyalist'
    elif r == 3 and f == 3 and m == 3:
        return 'needs_attention'
    elif r == 4 and f == 4 and m == 4:
        return 'at_risk'
    elif r >= 3 and f >= 3:
        return 'about_to_sleep'
    elif r == 4:
        return 'hibernating'
    else:
        return 'others'
