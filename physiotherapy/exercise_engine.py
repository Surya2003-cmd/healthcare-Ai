
def get_exercises(condition):
    exercises = {
        'Back Pain':['Cat Camel Stretch','Pelvic Tilt'],
        'Knee Pain':['Heel Slides','Straight Leg Raise']
    }
    return exercises.get(condition,['Walking'])
