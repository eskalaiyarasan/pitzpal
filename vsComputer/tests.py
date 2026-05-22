from django.test import TestCase

# Create your tests here.
#
# # Assuming your dictionary looks something like this:
x = {
    "y": [
        {"name": "Item A", "z": 42},
        {"name": "Item B", "z": 10},
        {"name": "Item C", "z": 99},
        {"name": "Item D", "z": 5},
    ]
}

# Sort the array in place (Lowest 'z' to Highest 'z')
x["y"].sort(key=lambda obj: obj["z"], reverse=True)

print(x)
